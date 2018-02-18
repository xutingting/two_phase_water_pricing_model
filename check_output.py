from utils import get_data, Candidate, to_original_order
from objective import Objective

if __name__ == '__main__':
    for i in range(100):
        sellers, buyers, edges = to_original_order(*get_data('data%d.txt'%i, distance_th=10))
        for prefix in ['balance', 'min_var', 'urr']:
            filename = 'output/' + prefix + str(i) + '.txt'
            records = eval(file(filename, 'r').readline())
            for (seller, buyer), (price, volume) in records:
                try:
                    assert (seller in sellers)
                    assert buyer in buyers, 'in file %s, buyer %d is not good' % (filename, buyer)
                    assert ((seller, buyer) in edges)
                    if volume > 1e-6:
                        assert (price > sellers[seller].price - 1e-6)
                        assert (price < buyers[buyer].price + 1e-6)
                except:
                    print filename

