from utils import change_name, VILLAGES

class DistanceConnectivity:
    '''
    This is a class for connectivity judgement.
    First, an instance of this class is created, Then, one can query whether two agents are connected by querying
     the order of the two agents.
    '''
    def __init__(self, distance_th=10):
        self.distances = self.load_distances()
        self.distance_th = distance_th

    @staticmethod
    def load_distances():
        distances = {}
        for line in file('area_info/distances.txt', 'r'):
            a, b, d = line.strip().split()
            a, b, d = int(a), int(b), float(d)
            distances[a, b] = d
        return distances

    def is_connect(self, a, b):
        return self.distances[a, b] <= self.distance_th


class CanalConnectivity:
    '''
    This is the class for connectivity based on canal locations
    '''
    def __init__(self, max_gap = 0):
        '''
        Load the relationships between villages are canals.
        :param max_gap: the maximum difference between canal numbers
        '''
        self.village_canals = {}
        self.max_gap = max_gap
        for line in file('area_info/village_canal_en.txt', 'r'):
            if len(line) < 2:
                continue
            name, canal = line.split()
            canal = int(canal)
            self.village_canals[change_name(name)] = canal
        assert set(self.village_canals.keys())==set(VILLAGES), "wrong villages"
        self.canals = [self.village_canals[village] for village in VILLAGES]

    def is_tradable(self, a, b):
        if b >= 5:
            b = 5
        return a * b == 0 or min([a, b]) == 5 or abs(a-b) <= self.max_gap

    def is_connect(self, a, b):
        return self.is_tradable(self.canals[a], self.canals[b])
