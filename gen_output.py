from objective import Objective
from utils import get_data, to_original_order
from connectivity import DistanceConnectivity

if __name__ == '__main__':
    for k_instance in range(100):
        sellers, buyers, edges = get_data('data%d.txt'%k_instance, DistanceConnectivity(10))
        _, _, ori_edges = to_original_order(sellers, buyers, edges)
        alg = Objective(sellers, buyers, edges)

        for obj in ['urr', 'min_var', 'balance']:
            filename = 'output/' + obj + str(k_instance) + '.txt'
            prices = alg.get_prices(obj)
            solution = zip(ori_edges, zip(prices, alg.fs))
            file(filename, 'w').write(str(solution))