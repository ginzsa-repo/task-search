import sys, os
import unittest


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import utils
from model import Team
from model import Vehicle
from optimizer import Optimizer
from distances import Distances


class TestCandidates(unittest.TestCase):

    def test_candidate(self):
        print('testing')

    

if __name__ == '__main__':
    unittest.main()