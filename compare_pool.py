from utils import Candidate, get_data, solve_opt_assignment, change_name, VILLAGES, output_to_csv, get_errors
import matplotlib.pyplot as plt
import sys
import numpy as np
from connectivity import DistanceConnectivity, CanalConnectivity

class Comparison:
    def __init__(self, k_instance = 0, connecter=DistanceConnectivity()):
        self.sellers, self.buyers, self.edges = get_data('data%d.txt'%k_instance,
                                                         connecter=connecter)

    def unique_price(self):
        '''
        only return the price.
        '''
        sellers, buyers, edges = self.sellers, self.buyers, self.edges
        sorted_sellers = sorted(sellers, cmp=lambda x, y: (x.price > y.price) * 2 - 1)
        sorted_buyers = sorted(buyers, cmp=lambda x, y: (y.price > x.price) * 2 - 1)
        if sorted_sellers[0].price >= sorted_buyers[0].price:
            return 0
        v_s, v_b = sorted_sellers[0].quantity, sorted_buyers[0].quantity
        p_s, p_b = 1, 1
        while p_s < len(sellers) and p_b < len(buyers):
            if v_s > v_b:
                if sorted_buyers[p_b].price <= sorted_sellers[p_s - 1].price:
                    break
                v_b += sorted_buyers[p_b].quantity
                p_b += 1
                continue
            if sorted_buyers[p_b - 1].price <= sorted_sellers[p_s].price:
                break
            v_s += sorted_sellers[p_s].quantity
            p_s += 1
        while p_s == len(sellers) and p_b < len(buyers) and sorted_buyers[p_b].price > sorted_sellers[p_s - 1].price:
            p_b += 1
        while p_b == len(buyers) and p_s < len(sellers) and sorted_sellers[p_s].price < sorted_buyers[p_b - 1].price:
            p_s += 1
        return (sorted_sellers[p_s - 1].price + sorted_buyers[p_b - 1].price) / 2

    def compare_sw(self):
        return solve_opt_assignment(self.sellers, self.buyers, self.edges)[0], self.pooled_exchzange()[0]

    def get_opt(self):
        return solve_opt_assignment(self.sellers, self.buyers, self.edges)[0]

    def pooled_exchzange(self):
        '''
        get the outcome of pooled exchange
        :return: the social welfare and flows on edges.
        '''
        sellers, buyers, edges, price = self.sellers, self.buyers, self.edges, self.unique_price()
        new_edges = [(x, y) for (x, y) in edges if sellers[x].price <= price and buyers[y].price >= price]
        sw, fs_tmp = solve_opt_assignment(sellers, buyers, new_edges)
        p = 0
        fs = []
        for x, y in self.edges:
            if sellers[x].price <= price and buyers[y].price >= price:
                fs.append(fs_tmp[p])
                p += 1
            else:
                fs.append(0)
        return sw, fs

    def plot(self, fs, title = None):
        '''
        plot the figure with volumes on it.
        :param fs: the flows on edges. the size equals to the size of edges.
        :return:
        '''
        # read the position of the villages.
        pos = {}
        for i in file('area_info/village_pos.txt', 'r'):
            name, p1, p2 = i[:-1].split()
            pos[change_name(name)] = (float(p1), float(p2))
        positions = [pos[i] for i in VILLAGES]
        f = file('area_info/map_data.txt', 'r')
        data = f.readlines()
        apps = {'*k': 1}
        las = {'r': 'trunk canal', 'b': 'main canal', 'g': 'lateral canal'}
        color_to_style = {'r': '-', 'b': '--', 'g': ':', '*': '*'}
        color_to_lw = {'r': 4, 'b': 3, 'g': 2}
        xs = []
        ys = []
        plt.clf()
        for linenum in range(len(data)):
            line = data[linenum]
            line = line[:-1].split(',')
            n = len(line) / 2
            s = line[-1]
            if line[-1] == '*':
                continue
            xs += [float(line[i * 2]) for i in range(n)]
            ys += [-(float(line[i * 2 + 1])) for i in range(n)]
            if s not in apps:
                apps[s] = 1
                plt.plot([float(line[i * 2]) for i in range(n)], [-(float(line[i * 2 + 1])) for i in range(n)], \
                         color_to_style[s] + 'g', label=las[s], linewidth=color_to_lw[s])
            else:
                plt.plot([float(line[i * 2]) for i in range(n)], [-(float(line[i * 2 + 1])) for i in range(n)],
                         color_to_style[s] + 'g', \
                         linewidth=color_to_lw[s])
        village_colors = {i:'k' for i in pos}
        for k, (x, y) in enumerate(self.edges):
            rx, ry = self.sellers[x].rank, self.buyers[y].rank
            plt.plot([positions[rx][0], positions[ry][0]], [-positions[rx][1], -positions[ry][1]], 'm', lw=fs[k]/4e4)
        for i in self.sellers:
            village_colors[VILLAGES[i.rank]] = 'r'
        for i in self.buyers:
            village_colors[VILLAGES[i.rank]] = 'b'
        plt.plot([pos[i][0] for i in pos], [-pos[i][1] for i in pos], '*k', label='non-trader', ms=6)
        ss = [VILLAGES[i.rank] for i in self.sellers]
        plt.plot([pos[i][0] for i in ss], [-pos[i][1] for i in ss], 'or', label='seller',ms=7)
        bs = [VILLAGES[i.rank] for i in self.buyers]
        plt.plot([pos[i][0] for i in bs], [-pos[i][1] for i in bs], 'ob', label='buyer', ms=7)
        plt.axis('equal')
        plt.axis('off')
        plt.legend(loc=3, numpoints=1)
        if title is not None:
            plt.savefig('figures/'+title+'.pdf', dpi=600)
        plt.show()

if __name__ == '__main__':
    if len(sys.argv) > 1 and '1' in sys.argv[1]:
        # This is a comparison on a special case
        tmp = Comparison(11)
        sw1, fs1 = solve_opt_assignment(tmp.sellers, tmp.buyers, tmp.edges)
        sw2, fs2 = tmp.pooled_exchzange()
        print sw1, sw2
        tmp.plot(fs1, 'Optimal assignment')
        tmp.plot(fs2, 'Pooled exchange')

    # analyze the influence of thresholds.
    if len(sys.argv) > 1 and '2' in sys.argv[1]:
        SW1 = []
        SW2 = []
        for th in range(3, 20, 3):
            distance_th = th
            sw1, sw2 = [], []
            for i in range(100):
                sw1_i, sw2_i = Comparison(i, DistanceConnectivity(th)).compare_sw()
                sw1.append(sw1_i)
                sw2.append(sw2_i)
            print sw1, sw2
            SW1.append(sw1)
            SW2.append(sw2)
        y1, y2 = np.mean(SW1, axis=1), np.mean(SW2, axis=1)
        plt.plot(range(3, 20, 3), y1, '.-', label='Walrasian equilibrium')
        plt.plot(range(3, 20, 3), y2, '>-', label='Pool exchange')
        plt.xticks(range(3, 20, 3), [str(i) for i in range(3, 20, 3)])
        plt.xlabel('Distance threshold (km)')
        plt.ylabel('Social welfare (RMB)')
        plt.legend(loc='lower right')
        plt.savefig('figures/distance_threshold.pdf', dpi=1200)
        plt.show()
        
    # Analyze the influence of the gap between canals.
    if len(sys.argv) > 1 and '3' in sys.argv[1]:
        SW1 = []
        SW2 = []
        for canal_distance in range(5):
            sw1, sw2 = [], []
            for i in range(100):
                sw1_i, sw2_i = Comparison(i, CanalConnectivity(canal_distance)).compare_sw()
                sw1.append(sw1_i)
                sw2.append(sw2_i)
            SW1.append(sw1)
            SW2.append(sw2)
            print 'if allow max canal gap is {}, the optimal is {} and the pool is {}'.format(canal_distance,
                                                                                              np.mean(sw1),
                                                                                              np.mean(sw2))
        y1, y2 = np.mean(SW1, axis=1), np.mean(SW2, axis=1)
        plt.plot(range(5), y1, '.-', label='Proposed model')
        plt.plot(range(5), y2, '>-', label='Pool exchange')
        plt.xticks(range(5), [str(i) for i in range(5)])
        plt.xlabel('Maximum tradable canal gap')
        plt.ylabel('Social welfare (RMB)')
        plt.legend(loc='lower right')
        plt.savefig('figures/canal_threshold.pdf', dpi=1200)
        plt.show()
        output_to_csv('canal_diff', {'distance':range(5), 'proposed model': y1, 'pool exchange': y2})


    if len(sys.argv) > 1 and '4' in sys.argv[1]:
        # This is a comparison on a special case
        for canal_distance in range(3):
            tmp = Comparison(1, CanalConnectivity(canal_distance))
            sw1, fs1 = solve_opt_assignment(tmp.sellers, tmp.buyers, tmp.edges)
            sw2, fs2 = tmp.pooled_exchzange()
            print sw1, sw2
            tmp.plot(fs1, 'Optimal_assignment_cd%d' % canal_distance)
            tmp.plot(fs2, 'Pooled_exchange_cd%d' % canal_distance)

    if len(sys.argv) > 1 and '5' in sys.argv[1]:
        PC1 = []  # percent change compared to pool exchange
        PC2 = []  # percent change compared to blockly pool exchange
        base2 = [Comparison(i, CanalConnectivity(0)).get_opt() for i in range(100)]
        for canal_distance in range(5):
            pc1, pc2 = [], []
            for i in range(100):
                sw1_i, sw2_i = Comparison(i, CanalConnectivity(canal_distance)).compare_sw()
                pc1.append(sw1_i * 100. / sw2_i - 100)
                pc2.append(sw1_i * 100 / base2[i] - 100)
            PC1.append(pc1)
            PC2.append(pc2)
            print 'if allow max canal gap is {}, the percent change based on pool exchange is {} and' \
                  ' the percent change based on blockly pool exchange is {}'.format(canal_distance,
                                                                                              np.mean(pc1),
                                                                                              np.mean(pc2))
        y1, y2 = np.mean(PC1, axis=1), np.mean(PC2, axis=1)
        plt.plot([0,4], [0, 0], 'k')
        plt.errorbar(range(5), y1, get_errors(PC1))
        plt.ylabel('Percent change')
        plt.xticks(range(5))
        plt.xlabel('Maximum tradable canal gap')
        plt.savefig('figures/improve_p.pdf', dpi=1200)
        plt.show()
        plt.clf()
        plt.plot([0, 4], [0, 0], 'k')
        plt.errorbar(range(5), y2, get_errors(PC2))
        plt.ylabel('Percent change')
        plt.xticks(range(5))
        plt.xlabel('Maximum tradable canal gap')
        plt.savefig('figures/improve_b.pdf', dpi=1200)
        plt.show()
        output_to_csv('improvement', {'distance': range(5), 'to pool': y1, 'to blockly': y2,
                                      'to pool error': get_errors(PC1), 'to blockly error': get_errors(PC2)})

    if len(sys.argv) > 1 and '6' in sys.argv[1]:
        SW1 = []  # The social welfares for different distances, two-phase
        SW2 = []  # for pool exchange
        SW3 = []  # for separate pool enchange
        for canal_distance in range(5):
            sw1, sw2, sw3 = [], [], []
            for i in range(100):
                sw1_i, sw2_i = Comparison(i, CanalConnectivity(canal_distance)).compare_sw()
                sw3_i = Comparison(i, CanalConnectivity(0)).get_opt()
                sw1.append(sw1_i)
                sw2.append(sw2_i)
                sw3.append(sw3_i)
            SW1.append(sw1)
            SW2.append(sw2)
            SW3.append(sw3)

            # Latex friendly outputs the answers.
            print '{distance} & {sw_opt:.2f} & {sw_pool:.2f} & {sw_separate:.2f} \\\\'.format(
                distance =canal_distance,
                sw_opt = np.mean(sw1),
                sw_pool = np.mean(sw2),
                sw_separate = np.mean(sw3)
            )
