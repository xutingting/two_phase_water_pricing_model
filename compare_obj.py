from utils import get_data, to_original_order, output_to_csv, get_confidence_interval
import numpy as np
import matplotlib.pyplot as plt
import sys
from connectivity import DistanceConnectivity, CanalConnectivity
from collections import OrderedDict

CASES = ['urr', 'min_var', 'balance']

if __name__ == '__main__':
    urr = []
    balance = []
    min_var = []
    for i in range(100):
        balance.append(eval(file('output/balance%d.txt' % i).readline()))
        urr.append(eval(file('output/urr%d.txt' % i).readline()))
        min_var.append(eval(file('output/min_var%d.txt' % i).readline()))

    # The first exp: plot the price distribution.
    if len(sys.argv) > 1 and '1' in sys.argv[1]:
        urr = []
        balance = []
        min_var = []
        for i in range(100):
            balance.append(eval(file('output/balance%d.txt' % i).readline()))
            urr.append(eval(file('output/urr%d.txt' % i).readline()))
            min_var.append(eval(file('output/min_var%d.txt' % i).readline()))
        ys = [[0] * 15 for i in range(3)]
        t_ticks = ['%.2lf' % (0.14 + i * 0.01) for i in range(13)]
        for k, data in enumerate([balance, urr, min_var]):
            show_prices = []
            for i in range(100):
                for _, (price, flow) in data[i]:
                    show_prices.append(price)
            for price in show_prices:
                price = int(round(price * 100)) - 14
                ys[k][price] += 1
        plt.xticks(range(13), t_ticks)
        # plt.plot(range(13), ys[1][:13], label='MUP-based balance')
        # plt.plot(range(13), ys[2][:13], label='Minimum variance')
        # plt.plot(range(13), ys[0][:13], label='Two-sided balance')
        plt.xlabel(r'Price (RMB/$m^3$)')
        st, en = 14, 27
        plt.bar([i - 0.3 for i in range(st, en)], ys[1][:13], 0.2, color='k',
                label='Threshold-based balance')
        plt.bar([i - 0.1 for i in range(st, en)], ys[2][:13], 0.2, color='darkgray',
                label='Minimize variance')
        plt.bar([i + 0.1 for i in range(st, en)], ys[0][:13], 0.2, hatch='//',
                color='white',
                label='Two-sided balance')
        plt.xticks(range(st, en), [str(i / 100.) for i in range(st, en)])
        plt.xlim((st - 1, en))
        plt.ylabel('Number of edges')
        print 'the total number of edges ', sum(ys[0])
        plt.legend()
        plt.savefig('figures/dis.pdf')
        output_to_csv('price_distribution',
                      OrderedDict([
                          ('price', t_ticks),
                          ('Two-sided balance', ys[0][:13]),
                          ('Threshold-based balance', ys[1][:13]),
                          ('Minimum variance', ys[2][:13])
                      ]))

    # collect the utilities for each agent, instance pair.
    urr_u, balance_u, min_var_u = np.zeros((73, 100)), np.zeros((73, 100)), np.zeros((73, 100))
    for i in range(100):
        for data, utility in [(balance, balance_u), (urr, urr_u), (min_var, min_var_u)]:
            prices = {}
            tmp = eval(file('price_data/data%d.txt' % i, 'r').readline())
            for k, (case, price, volume) in enumerate(tmp):
                prices[k] = price
            for (seller, buyer), (price, volume) in data[i]:
                if volume > 1e-6:
                    assert volume * (price - prices[seller] + 1e-6) > 0
                    assert volume * (prices[buyer] - price + 1e-6) > 0
                    utility[seller, i] += volume * (price - prices[seller] + 1e-6)
                    utility[buyer, i] += volume * (prices[buyer] - price + 1e-6)
    urr_sum, balance_sum, min_var_sum = np.sum(urr_u, 1), np.sum(balance_u, 1), np.sum(min_var_u, 1)

    # rank the three objective functions
    if len(sys.argv) > 1 and '2' in sys.argv[1]:
        ranks = np.zeros((3, 3))  # urr, balance, min_var * 1st, 2nd, 3rd
        for i in range(73):
            tmp = sorted([(0, urr_sum[i]), (1, balance_sum[i]), (2, min_var_sum[i])], key=lambda x: x[1], reverse=True)
            for rank, (case, _) in enumerate(tmp):
                ranks[case, rank] += 1
        for case, casename in enumerate(CASES):
            for rank in range(3):
                print casename, rank, ranks[case, rank]

    # plot the optimal choice for  all the agents.
    if len(sys.argv) > 1 and '3' in sys.argv[1]:
        param = sys.argv[2] if len(sys.argv) > 2 else 's'
        # The first step is to obtain the average price and volume.
        total_price = [0] * 73
        total_volume = [1e-6] * 73  # to avoid divide 0.
        for k_instance in range(100):
            instance = eval(file('price_data/data%d.txt' % k_instance, 'r').readline())
            for i in range(73):
                if instance[i][0] == param:
                    if urr_u[i, k_instance] < -0.1:
                        print i, k_instance, urr_u[i, k_instance]
                        raise StandardError('expect positive')
                    total_price[i] += instance[i][1] * instance[i][2]
                    total_volume[i] += instance[i][2]
        rank_balance, rank_urr, rank_min_var = [], [], []
        for i in range(73):
            if i % 20 == 0:
                print i, urr_sum[i], balance_sum[i], min_var_sum[i]
            if urr_sum[i] >= balance_sum[i] and urr_sum[i] >= min_var_sum[i]:
                rank_urr.append(i)
            if urr_sum[i] <= balance_sum[i] and balance_sum[i] >= min_var_sum[i]:
                rank_balance.append(i)
            if min_var_sum[i] >= balance_sum[i] and urr_sum[i] <= min_var_sum[i]:
                rank_min_var.append(i)
        plt.plot([total_price[i] / total_volume[i] for i in rank_urr], [total_volume[i] for i in rank_urr], 'o',
                 label='URR-based balance')
        plt.plot([total_price[i] / total_volume[i] for i in rank_balance], [total_volume[i] for i in rank_balance], '*',
                 label='Two-side balance')
        plt.plot([total_price[i] / total_volume[i] for i in rank_min_var], [total_volume[i] for i in rank_min_var], '>',
                 label='Minimum variance')
        plt.legend()
        plt.xlim((0.1, 0.25))
        plt.xlabel('Average %s (yuan)'%('bid' if param == 'b' else 'ask'))
        plt.ylabel(r'Volume ($m^3$)')
        plt.savefig('figures/%s_choice.pdf'%('buyer' if param == 'b' else 'seller'), dpi=1200)
        plt.show()

    # the bar graph for the number of instances and preferred objective function.
    if len(sys.argv) > 1 and '4' in sys.argv[1]:
        param = sys.argv[2] if len(sys.argv) > 2 else 's'
        seller_basket = {case:[0] * 30 for case in CASES}
        buyer_basket = {case: [0] * 30 for case in CASES}
        to_basket = lambda x: int(x * 100)  # map the prices to the baskets
        for k_instance in range(100):
            sellers, buyers, edges = to_original_order(*get_data('data%d.txt' % k_instance,
                                                                 connecter=CanalConnectivity()))
            for (baskets, group) in [(seller_basket, sellers), (buyer_basket, buyers)]:
                for agent in group:
                    tmp = sorted([(0, urr_u[agent][k_instance]), (1, min_var_u[agent][k_instance]),
                                  (2, balance_u[agent][k_instance])], key=lambda x: x[1], reverse=True)
                    if tmp[0][1] < 1e-6:  # This sller does not gain utility in this round.
                        continue
                    basket = to_basket(group[agent].price)
                    if tmp[0][1] > tmp[1][1]:  # Only one best
                        baskets[CASES[tmp[0][0]]][basket] += 1
                    elif tmp[1][1] > tmp[2][1]:  # two best
                        baskets[CASES[tmp[0][0]]][basket] += 0.5
                        baskets[CASES[tmp[1][0]]][basket] += 0.5
                    else:  #three best
                        baskets[CASES[tmp[0][0]]][basket] += 0.33
                        baskets[CASES[tmp[1][0]]][basket] += 0.33
                        baskets[CASES[tmp[2][0]]][basket] += 0.33
        st, en =10, 24
        if param == 'b':
            baskets = buyer_basket
            xlabel = 'Bid (RMB)'
            figure_name = 'buyer_preference.pdf'
            st, en = 14, 28
        else:
            baskets = seller_basket
            xlabel = 'Ask (RMB)'
            figure_name = 'seller_preference.pdf'
            st, en = 10, 24
        plt.bar([i-0.3 for i in range(st, en)], [baskets['urr'][i] for i in range(st, en)], 0.2, color='k',
                label = 'Threshold-based balance')
        plt.bar([i - 0.1 for i in range(st, en)], [baskets['min_var'][i] for i in range(st, en)], 0.2, color = 'darkgray',
                label='Minimize variance')
        plt.bar([i + 0.1 for i in range(st, en)], [baskets['balance'][i] for i in range(st, en)], 0.2, hatch='//', color='white',
                label='Two-sided balance')
        plt.xticks(range(st, en), [str(i/100.) for i in range(st, en)])
        plt.xlim((st-1, en))
        plt.xlabel(xlabel)
        plt.ylabel('Number of selection')
        plt.legend()
        plt.savefig('figures/'+figure_name, dpi=1200)
        plt.show()
        output_to_csv(param+'_preference', OrderedDict([('price', [str(i/100.) for i in range(st, en)]),
                                                        ('Threshold-based balance', [baskets['urr'][i] for i in range(st, en)]),
                                                        ('Minimize variance', [baskets['min_var'][i] for i in range(st, en)]),
                                                        ('Two-sided balance', [baskets['balance'][i] for i in range(st, en)])]))

    if len(sys.argv) > 1 and '5' in sys.argv[1]:
        import scipy.stats as stats
        case_to_utility = {
            'urr': urr_u,
            'min_var': min_var_u,
            'balance': balance_u,
        }
        for case1 in CASES:
            for case2 in CASES:
                if case1 == case2:
                    continue
                print 'comparing', case1, case2
                u1 = case_to_utility[case1]
                u2 = case_to_utility[case2]
                ratios = []
                seller_ratios = []
                buyer_ratios = []
                for k_instance in range(100):
                    instance = eval(file('price_data/data%d.txt' % k_instance, 'r').readline())
                    prefer1 = 0
                    prefer2 = 0
                    prefer1s = 0
                    prefer2s = 0
                    prefer1b = 0
                    prefer2b = 0
                    for i in range(73):
                        role = instance[i][0]
                        if u1[i][k_instance] > u2[i][k_instance]:
                            prefer1 += 1
                            if role == 's':
                                prefer1s += 1
                            else:
                                prefer1b += 1
                        elif u1[i][k_instance] < u2[i][k_instance]:
                            prefer2 += 1
                            if role == 's':
                                prefer2s += 1
                            else:
                                prefer2b += 1
                        else:
                            prefer1 += 0.5
                            prefer2 += 0.5
                            prefer1s += 0.5
                            prefer2s += 0.5
                            prefer1b += 0.5
                            prefer2b += 0.5

                    ratios.append(1.0 * prefer1 / prefer2)
                    seller_ratios.append(1.0 * prefer1s / prefer2s)
                    buyer_ratios.append(1.0 * prefer1b / prefer2b)
                print 'for all'
                get_confidence_interval(ratios)
                print 'p value:', stats.ttest_1samp(ratios, 1.0)
                # print 'for sellers'
                # get_confidence_interval(seller_ratios)
                # print 'p value:', stats.ttest_1samp(seller_ratios, 1.0)
                # print 'for buyers'
                # get_confidence_interval(buyer_ratios)
                # print 'p value:', stats.ttest_1samp(buyer_ratios, 1.0)


