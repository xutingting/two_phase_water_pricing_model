VILLAGES = ['songshucun', 'longquancun', 'xiwancun', 'sishilicun', 'shangerqicun', \
            'ershilicun', 'honglincun', 'yawancun', 'gaosicun', 'yingpancun', 'hongxingcun', \
            'donghucun', 'chenlucun', 'hongxiangcun', 'yangoucun', 'yichengcun', \
            'houxingcun', 'zhizhaicun', 'houjicun', 'xiazhaicun', 'zhongbaocun', \
            'shangsanqicun', 'huaishucun', 'fenglecun', 'yousanbacun', 'shuangzhuangcun', \
            'shanwancun', 'lianhuashancun', 'duolangcun', 'huatingcun', 'zagoucun', \
            'changlongcun', 'longkoucun', 'kangningcun', 'chenchuncun', 'xinqiaocun', \
            'sanzhongcun', 'shangliucun', 'toupaicun', 'beihecun', 'qianxingcun', \
            'hongsicun', 'qiaojiasicun', 'xinhecun', 'tuanzhuangcun', 'quangoucun', \
            'yongfengcun', 'dalucun', 'xiaozhaicun', 'keqicun', 'shenglicun', 'jienaoqicun', \
            'tianquancun', 'xinzhaicun', 'nanhecun', 'fengliangcun', 'wuhecun', 'duoyuncun', \
            'sibaqiaocun', 'qinglincun', 'jinshancun', 'maogoucun', 'shatancun', 'jiehecun', \
            'yingercun', 'zhaizicun', 'beilingcun', 'huaixicun', 'xingoucun', 'shajincun', \
            'huaiancun', 'lujiagoucun', 'wuaicun']


class Candidate:
    def __init__(self, price, quantity, rank = -1):
        '''

        :param price: the bid or ask of a trader
        :param quantity: the maximum volume a trader wants to trade
        :param rank: the rank of the trader in the original dataset.
        '''
        self.price = price
        self.quantity = quantity
        self.rank = rank

    def __str__(self):
        return 'Candidate(price=%lf, quantity=%lf, rank=%d)' % (self.price, self.quantity, self.rank)

    def __le__(self, other):
        return self.price < other.price


def change_name(s):
    ori=['sanqicun','jienaocun','yousancun','shangercun','honglinnongchang','quijiazhuangcun',\
    'qiaojiacun','honglinlinchang','lianhuacun','qiaosicun','xinhe']
    new=['shangsanqicun','jienaoqicun','yousanbacun','shangerqicun','honglincun','qiujiazhuang',\
    'qiaojiasicun','honglincun','lianhuashancun','qiaojiasicun','xinhecun']
    if s in ori:
        return new[ori.index(s)]
    return s


def get_data(filename, connecter):
    '''
    return sellers, buyers and edges of a data. Sellers and buyers are list of candidates
    :param filename: the filename for the current data.
    :param connecter: an instance whose is_connect function can judge whether two villages are physically connected.
    :return:
    '''
    f = file('price_data/' + filename, 'r')
    data = eval(f.readline())
    f.close()
    sellers = [Candidate(price, quantity, k) for k, (case, price, quantity) in enumerate(data) if case == 's']
    buyers = [Candidate(price, quantity, k) for k, (case, price, quantity) in enumerate(data) if case == 'b']
    edges = [(i, j) for i, seller in enumerate(sellers) for j, buyer in enumerate(buyers)
             if connecter.is_connect(seller.rank, buyer.rank) and seller.price < buyer.price]
    return sellers, buyers, edges


def to_original_order(sellers, buyers, edges):
    '''
    The input should be exact the format of the output of get_data.
    :param sellers: the candidates for the sellers
    :param buyers: the candidates of the buyers
    :param edges: edges numbered by the order in the last two lists.
    :return: sellers, buyers, edges. sellers and buyers and map from rank to the candidate and the edges follow
     the orginal order
    '''
    seller_ranks = [i.rank for i in sellers]
    sellers = {i.rank:i for i in sellers}
    buyer_ranks = [i.rank for i in buyers]
    buyers = {i.rank:i for i in buyers}
    edges = [(seller_ranks[i], buyer_ranks[j]) for (i,j) in edges]
    return sellers, buyers, edges


def solve_opt_assignment(sellers, buyers, edges):
    '''
    Solving the assignment with maximum social welfare.
    :param sellers: the set of sellers
    :param buyers: the set of buyers
    :param edges: the edges (int, int)
    :return: the optimal social welfare and the volumes on all the edges edges.
    '''
    import pulp as pp
    prob = pp.LpProblem('max social welfare', pp.LpMaximize)
    f = pp.LpVariable.dict('f', range(len(edges)), 0)
    prob += pp.lpSum([(buyers[b].price - sellers[a].price) * f[k] for k, (a, b) in enumerate(edges)])
    for i, seller in enumerate(sellers):
        attached = []
        for k, edge in enumerate(edges):
            if edge[0] == i:
                attached.append(k)
        if len(attached) == 0:
            continue
        prob += pp.lpSum([f[k] for k in attached]) <= sellers[i].quantity
    for i, buyer in enumerate(buyers):
        attached = []
        for k, edge in enumerate(edges):
            if edge[1] == i:
                attached.append(k)
        if len(attached) == 0:
            continue
        prob += pp.lpSum([f[k] for k in attached]) <= buyers[i].quantity
    prob.solve()
    fs = []  # the flow on the edges.
    for i, edge in enumerate(edges):
        fs.append(pp.value(f[i]))
    return sum([(buyers[b].price - sellers[a].price) * fs[k] for k, (a, b) in enumerate(edges)]), fs


def convert_village_canal_file():
    '''
    This function is used to convert the village_canal file. Do not use it when there is villae_canal_en.txt
    :return:
    '''
    import hanzi2pinyin
    import codecs
    infile = codecs.open('area_info/village_canal.txt', encoding='utf-8')
    outfile = file('area_info/village_canal_en.txt', 'w')
    for line in infile:
        print line
        name, canal = hanzi2pinyin.hanzi2pinyin(line).split()
        print name
        outfile.write('{} {}\n'.format(name, canal))
    outfile.close()


def output_to_csv(filename, data):
    f = file('csv_files/{}.csv'.format(filename), 'w')
    f.write(','.join(data.keys()) + '\n')
    n = len(data.values()[0])
    for i in range(n):
        f.write(','.join([str(data[key][i]) for key in data]) + '\n')
    f.close()


def get_errors(datas, confidence=0.95):
    import numpy as np
    import scipy as sp
    import scipy.stats

    errors = []
    for data in datas:
        a = 1.0 * np.array(data)
        n = len(a)
        m, se = np.mean(a), scipy.stats.sem(a)
        h = se * sp.stats.t._ppf((1+confidence)/2., n-1)
        errors.append(h)
    return errors

def get_confidence_interval(a, confidence = 0.95):
    import numpy as np
    import scipy as sp
    import scipy.stats
    a = np.array(a) * 1.0
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * sp.stats.t._ppf((1 + confidence) / 2., n - 1)
    print m - h, m + h