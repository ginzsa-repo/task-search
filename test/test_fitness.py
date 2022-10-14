import sys, os
import unittest


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model import JobsSequence

from distances import Distances

from test_optimizer import load_distances_matrix, get_team
from fitness import job_fitness

class TestFitness(unittest.TestCase):
    def test_calculate_job_fitness(self):
        # given a distance object with matrix is created
        matrix = load_distances_matrix()
        team = get_team()
        distances = Distances(distances=matrix)
        config = {'tabu_size': 4, 'iterations': 10, 'item_weight':10_000, 'time_weight': 1}

        # when validate distances for vehicle jobs
        jobs = [('DOCK_134', 1), ('DOCK_280', 4), ('DOCK_399', 4), ('DOCK_301', 13), ('DOCK_155', 13)]
        start_end = ('DEPOT_1', 0)
        jobs_seq = JobsSequence(jobs=jobs, start=start_end, end=start_end)
        rs = job_fitness(config, distances, jobs_seq, team)

        # then result should be true
        self.assertEqual(rs, 220491)

    # DP (DEPOT_1) [DOCK_280,4] -> [DOCK_399,4] -> [DOCK_301,13] -> [DOCK_155,13] -> DP (DEPOT_1)
    def test_calculate_job_fitness_pre_insert(self):
        # given a distance object with matrix is created
        matrix = load_distances_matrix()
        team = get_team()
        distances = Distances(distances=matrix)
        config = {'tabu_size': 4, 'iterations': 10, 'item_weight':10_000, 'time_weight': 1}

        # when validate distances for vehicle jobs
        jobs = [('DOCK_280', 4), ('DOCK_399', 4), ('DOCK_301', 13), ('DOCK_155', 13)]
        start_end = ('DEPOT_1', 0)
        jobs_seq = JobsSequence(jobs=jobs, start=start_end, end=start_end)
        rs = job_fitness(config, distances, jobs_seq, team)

        # then result should be true
        self.assertEqual(rs, 222292.0)

    def test_calculate_job_fitness_post_insert(self):
        # given a distance object with matrix is created
        matrix = load_distances_matrix()
        team = get_team()
        distances = Distances(distances=matrix)
        config = {'tabu_size': 4, 'iterations': 10, 'item_weight':10_000, 'time_weight': 1}

        # when validate distances for vehicle jobs
        jobs = [('DOCK_11', 1), ('DOCK_280', 4), ('DOCK_399', 4), ('DOCK_301', 13), ('DOCK_155', 13)]
        start_end = ('DEPOT_1', 0)
        jobs_seq = JobsSequence(jobs=jobs, start=start_end, end=start_end)
        rs = job_fitness(config, distances, jobs_seq, team)

        # then result should be true
        self.assertEqual(rs, 218965.0)

if __name__ == '__main__':
    unittest.main()