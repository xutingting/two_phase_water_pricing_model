from utils import *
from objective import Objective


def generate_case():
    '''
    This is a function generating the data for a special case. with 3 sellers and 2 buyers
    :return: the list of sellers, the list of buyers, the edges between them.
    '''
    sellers = [Candidate(0.16, 10), Candidate(0.18, 10), Candidate(0.2, 10)]
    buyers = [Candidate(0.19, 13), Candidate(0.21, 13)]
    edges = [(0, 0), (1, 0), (1, 1), (2,1)]
    return sellers, buyers, edges

sw, vols = solve_opt_assignment(*generate_case())
print "social welfare and volumes on each edge", sw, vols
print "The prices on each edge", Objective(*generate_case()).min_variance()