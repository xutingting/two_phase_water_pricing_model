from unittest import TestCase
from objective import Objective
from utils import Candidate


class TestObjective(TestCase):
    def test_unfulfilled_agents(self):
        sellers = [Candidate(0, 1), Candidate(0, 0.4)]
        buyers = [Candidate(0, 1.2), Candidate(0, 0.5)]
        edges = [(0, 0), (1, 1)]
        fs = [1, 0.3]
        ans = Objective.unfulfilled_agents(sellers, buyers, edges, fs)
        self.assertEqual(ans[0], [1], str(ans))
        self.assertEqual(ans[1], [0, 1], str(ans))
