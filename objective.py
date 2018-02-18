from utils import solve_opt_assignment
import cplex

class Objective:
    def __init__(self, sellers, buyers, edges):
        self.sellers = sellers
        self.buyers = buyers
        self.edges = edges
        self.sw, self.fs = solve_opt_assignment(sellers, buyers, edges)
    
    @staticmethod
    def unfulfilled_agents(sellers, buyers, edges, fs):
        sellers_remain = [seller.quantity for seller in sellers]
        buyers_remain = [buyer.quantity for buyer in buyers]
        for k, (x, y) in enumerate(edges):
            sellers_remain[x] -= fs[k]
            buyers_remain[y] -= fs[k]
        return [i for i, remain in enumerate(sellers_remain) if remain > 0.01], \
               [i for i, remain in enumerate(buyers_remain) if remain > 0.01]
        
    def urr_based_balance(self):
        sellers, buyers, edges, fs = self.sellers, self.buyers, self.edges, self.fs
        prob = cplex.Cplex()
        prob.variables.add(obj=[0] * len(sellers), lb=[0] * len(sellers),
                           names=['r_s%d' % i for i in range(len(sellers))])
        prob.variables.add(obj=[0] * len(buyers), lb=[0] * len(buyers),
                           names=['r_b%d' % i for i in range(len(buyers))])
        prob.variables.add(obj=[0] * len(edges), lb=[0] * len(edges), names=['p%d' % i for i in range(len(edges))])

        # Unfulfilled agents' urr are 0
        unfulfilled_sellers, unfulfilled_buyers = self.unfulfilled_agents(sellers, buyers, edges, fs)
        total_len = len(unfulfilled_buyers) + len(unfulfilled_sellers)
        if total_len > 0:
            prob.linear_constraints.add([[['r_s%d'%i for i in unfulfilled_sellers] +
                                             ['r_b%d'%i for i in unfulfilled_buyers],
                                          [1] * total_len]],
                                        'E',
                                        [0])
        has_flow = []
        not_full = []
        for k, (x, y) in enumerate(edges):
            if fs[k] > 1e-3:
                has_flow.append(k)
            if fs[k] + 1e-3 < min(sellers[x].quantity, buyers[y].quantity):
                not_full.append(k)
        prob.linear_constraints.add([[['p%d' % i, 'r_s%d' % edges[i][0]], [1, -1]] for i in has_flow],
                                    'G' * len(has_flow), [sellers[edges[i][0]].price for i in has_flow])
        prob.linear_constraints.add([[['p%d' % i, 'r_b%d' % edges[i][1]], [1, 1]] for i in has_flow],
                                    'L' * len(has_flow), [buyers[edges[i][1]].price for i in has_flow])
        prob.linear_constraints.add([[['p%d' % i, 'r_s%d' % edges[i][0]], [1, -1]] for i in not_full],
                                    'L' * len(not_full), [sellers[edges[i][0]].price for i in not_full])
        prob.linear_constraints.add([[['p%d' % i, 'r_b%d' % edges[i][1]], [1, 1]] for i in not_full],
                                    'G' * len(not_full), [buyers[edges[i][1]].price for i in not_full])
        prob.linear_constraints.add(
            [[['p%d' % i, 'r_s%d' % x, 'r_b%d' % y], [1, -0.5, 0.5]] for i, (x, y) in enumerate(edges)],
            'E' * len(edges), [0.5 * (sellers[x].price + buyers[y].price) for (x, y) in edges])
        prob.solve()
        return prob.solution.get_values()[len(sellers) + len(buyers):]

    def two_side_balance(self):
        sellers, buyers, edges, fs = self.sellers, self.buyers, self.edges, self.fs
        prob = cplex.Cplex()
        prob.variables.add(obj=[0] * len(sellers), lb=[0] * len(sellers),
                           names=['r_s%d' % i for i in range(len(sellers))])
        prob.variables.add(obj=[0] * len(buyers), lb=[0] * len(buyers),\
                           names=['r_b%d' % i for i in range(len(buyers))])
        prob.variables.add(obj=[-2 * (sellers[x].price + buyers[y].price) * fs[k] for k, (x, y) in enumerate(edges)],
                           lb=[0] * len(edges), names=['p%d' % i for i in range(len(edges))])
        # Unfulfilled agents' urr are 0
        unfulfilled_sellers, unfulfilled_buyers = self.unfulfilled_agents(sellers, buyers, edges, fs)
        total_len = len(unfulfilled_buyers) + len(unfulfilled_sellers)
        if total_len > 0:
            prob.linear_constraints.add([[['r_s%d' % i for i in unfulfilled_sellers] +
                                          ['r_b%d' % i for i in unfulfilled_buyers],
                                          [1] * total_len]],
                                        'E',
                                        [0])

        has_flow = []
        not_full = []
        sellers_f = [0] * len(sellers)
        buyers_f = [0] * len(buyers)
        for i, (x, y) in enumerate(edges):
            sellers_f[x] += fs[i]
            buyers_f[y] += fs[i]
        for k, (x, y) in enumerate(edges):
            if fs[k] > 1e-3:
                has_flow.append(k)
            if fs[k] + 1e-3 < min(sellers[x].quantity, buyers[y].quantity):
                not_full.append(k)
        poors = ['r_s%d' % k for k in range(len(sellers)) if sellers_f[k] < 1e-3] + ['r_b%d' % k for k in
                                                                                     range(len(buyers)) if
                                                                                     buyers_f[k] < 1e-3]
        prob.linear_constraints.add([[['p%d' % i, 'r_s%d' % edges[i][0]], [1, -1]] for i in has_flow],
                                    'G' * len(has_flow), [sellers[edges[i][0]].price for i in has_flow])
        prob.linear_constraints.add([[['p%d' % i, 'r_b%d' % edges[i][1]], [1, 1]] for i in has_flow],
                                    'L' * len(has_flow), [buyers[edges[i][1]].price for i in has_flow])
        prob.linear_constraints.add([[['p%d' % i, 'r_s%d' % edges[i][0]], [1, -1]] for i in not_full],
                                    'L' * len(not_full), [sellers[edges[i][0]].price for i in not_full])
        prob.linear_constraints.add([[['p%d' % i, 'r_b%d' % edges[i][1]], [1, 1]] for i in not_full],
                                    'G' * len(not_full), [buyers[edges[i][1]].price for i in not_full])
        prob.linear_constraints.add([[poors, [1] * len(poors)]], 'E', [0])
        prob.objective.set_quadratic_coefficients([['p%d' % i, 'p%d' % i, 4 * fs[i]] for i in range(len(edges))])
        prob.solve()
        return prob.solution.get_values()[len(sellers) + len(buyers):]

    def min_variance(self):
        sellers, buyers, edges, fs = self.sellers, self.buyers, self.edges, self.fs
        prob = cplex.Cplex()
        prob.variables.add(obj=[0] * len(sellers), lb=[0] * len(sellers),
                           names=['r_s%d' % i for i in range(len(sellers))])
        prob.variables.add(obj=[0] * len(buyers), lb=[0] * len(buyers),\
                           names=['r_b%d' % i for i in range(len(buyers))])
        prob.variables.add(obj=[0] * len(edges), lb=[0] * len(edges), names=['p%d' % i for i in range(len(edges))])
        # Unfulfilled agents' urr are 0
        unfulfilled_sellers, unfulfilled_buyers = self.unfulfilled_agents(sellers, buyers, edges, fs)
        total_len = len(unfulfilled_buyers) + len(unfulfilled_sellers)
        if total_len > 0:
            prob.linear_constraints.add([[['r_s%d' % i for i in unfulfilled_sellers] +
                                          ['r_b%d' % i for i in unfulfilled_buyers],
                                          [1] * total_len]],
                                        'E',
                                        [0])

        has_flow = []
        not_full = []
        for k, (x, y) in enumerate(edges):
            if fs[k] > 1e-3:
                has_flow.append(k)
            if fs[k] + 1e-3 < min(sellers[x].quantity, buyers[y].quantity):
                not_full.append(k)
        prob.linear_constraints.add([[['p%d' % i, 'r_s%d' % edges[i][0]], [1, -1]] for i in has_flow],
                                    'G' * len(has_flow), [sellers[edges[i][0]].price for i in has_flow])
        prob.linear_constraints.add([[['p%d' % i, 'r_b%d' % edges[i][1]], [1, 1]] for i in has_flow],
                                    'L' * len(has_flow), [buyers[edges[i][1]].price for i in has_flow])
        prob.linear_constraints.add([[['p%d' % i, 'r_s%d' % edges[i][0]], [1, -1]] for i in not_full],
                                    'L' * len(not_full), [sellers[edges[i][0]].price for i in not_full])
        prob.linear_constraints.add([[['p%d' % i, 'r_b%d' % edges[i][1]], [1, 1]] for i in not_full],
                                    'G' * len(not_full), [buyers[edges[i][1]].price for i in not_full])
        prob.variables.add(obj=[0], names=['p_mean'])
        prob.linear_constraints.add(
            [[['p%d' % i for i in range(len(edges))] + ['p_mean'], [1] * len(edges) + [-len(edges)]]], 'E', [0])
        prob.objective.set_sense(prob.objective.sense.minimize)
        prob.objective.set_quadratic_coefficients([['p%d' % i, 'p%d' % i, 1] for i in range(len(edges))])
        prob.objective.set_quadratic_coefficients([['p_mean', 'p_mean', len(edges)]])
        prob.objective.set_quadratic_coefficients([['p%d' % i, 'p_mean', -1] for i in range(len(edges))])
        prob.solve()
        return prob.solution.get_values()[len(sellers) + len(buyers):-1]

    def get_prices(self, obj):
        obj_map = {'urr': self.urr_based_balance,
                   'min_var': self.min_variance,
                   'balance': self.two_side_balance}
        return obj_map[obj]()