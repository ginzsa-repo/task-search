import sys, os
import unittest


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import utils
from model import Team
from model import Vehicle
from model import JobsSequence
from optimizer import Optimizer
from distances import Distances

from test_optimizer import load_distances_matrix, get_team, get_vehicle
from validation import is_cadidate_valid, is_distance_valid_for_job_vehicle, is_journey_capacity_within_vehicle_constrain, is_journey_time_within_team_constrains, is_total_journey_time_within_team_constrains, is_single_journey_time_within_team_constrains
'''
[DOCK_101,3]
DP (DEPOT_1) [DOCK_280,4] -> [DOCK_399,4] -> [DOCK_301,13] -> [DOCK_155,13] -> DP (DEPOT_1)
'''
class TestValidation(unittest.TestCase):

    def test_is_distance_invalid_jobs(self):
        # given a distance object with matrix is created
        matrix = load_distances_matrix()
        team = get_team()
        distances = Distances(distances=matrix)

        # when validate distances for vehicle jobs
        jobs = [('DOCK_A', 3), ('DOCK_B', 4), ('DOCK_C', 6), ('DOCK_D', 1)]
        jobs_seq = JobsSequence(jobs=jobs, start=None, end=None)
        rs = is_distance_valid_for_job_vehicle(distances, jobs_seq, team)

        # then result should be true
        self.assertEqual(rs, False)

    def test_is_distance_valid_for_job_vehicle(self):
        # given a distance object with matrix is created
        matrix = load_distances_matrix()
        team = get_team()
        distances = Distances(distances=matrix)

        # when validate distances for vehicle jobs in test data
        jobs = [('DOCK_328', 3), ('DOCK_210', 4), ('DOCK_60', 6), ('DOCK_267', 1)]
        jobs_seq = JobsSequence(jobs=jobs, start=None, end=None)
        rs = is_distance_valid_for_job_vehicle(distances, jobs_seq, team)

        # then result should be true
        self.assertEqual(rs, True)

    def test_is_journey_capacity_within_vehicle_constrain(self):

        # given a team with a vehicle assigned to it
        team = get_team()

        # when validate distances for vehicle jobs in test data
        jobs = [('DOCK_328', 3), ('DOCK_210', 4), ('DOCK_60', 6), ('DOCK_267', 1)]
        jobs_seq = JobsSequence(jobs=jobs, start=None, end=None)

        rs = is_journey_capacity_within_vehicle_constrain(jobs_seq, team.vehicle)

        # then result should be true
        self.assertEqual(rs, True)

    def test_is_journey_capacity_within_vehicle_constrain_real(self):

        # given a team with a vehicle assigned to it
        team = get_team()

        # when validate distances for vehicle jobs in real test data
        jobs = jobs = [('DOCK_101', 3), ('DOCK_280', 4), ('DOCK_399', 4), ('DOCK_301', 13), ('DOCK_155', 13)]
        start_end = ('DEPOT_1', 0)
        jobs_seq = JobsSequence(jobs=jobs, start=start_end, end=start_end)

        rs = is_journey_capacity_within_vehicle_constrain(jobs_seq, team.vehicle)

        # then result should be false
        self.assertEqual(rs, False)

    def test_is_journey_capacity_outside_of_vehicle_constrain(self):

        # given a team with a vehicle assigned to it
        team = get_team()

        # when validate distances for vehicle jobs in test data (note: total 21 items!)
        jobs = [('DOCK_328', 10), ('DOCK_210', 4), ('DOCK_60', 6), ('DOCK_267', 1)]
        jobs_seq = JobsSequence(jobs=jobs, start=None, end=None)

        rs = is_journey_capacity_within_vehicle_constrain(jobs_seq, team.vehicle)
        
        # then result should be false
        self.assertEqual(rs, True)

    def test_is_journey_outside_of_time_team_constrains(self):
        # given a distance object with matrix is created
        matrix = load_distances_matrix()
        team = get_team()
        distances = Distances(distances=matrix)

        # when validate distances for vehicle jobs in test data
        jobs = [('DOCK_328', 3), ('DOCK_210', 4), ('DOCK_60', 6), ('DOCK_267', 1)]
        start_end = ('DEPOT_1', 0)
        jobs_seq = JobsSequence(jobs=jobs, start=start_end, end=start_end)
        rs = is_journey_time_within_team_constrains(distances, jobs_seq, team)

        # then result should be false
        self.assertEqual(rs, True)

    def test_is_single_journey_time_within_team_constrains_real(self):
        # given a distance object with matrix is created, team with small time constrain
        matrix = load_distances_matrix()
        distances = Distances(distances=matrix)
        vehicle = get_vehicle()
        # create team with big single journey time to comply with distance test data
        team = Team(vehicle=vehicle, time_available_sec=25200, max_single_journey_time_sec=18000, starting_items_on_board=0)
        
        # when validate distances for vehicle jobs in real test data
        jobs = [('DOCK_11', 1), ('DOCK_280', 4), ('DOCK_399', 4), ('DOCK_301', 13), ('DOCK_155',13)]
        start_end = ('DEPOT_1', 0)
        jobs_seq = JobsSequence(jobs=jobs, start=start_end, end=start_end)
        rs = is_journey_time_within_team_constrains(distances, jobs_seq, team)
        # then result should be ...
        self.assertEqual(rs, True)

    def test_is_journey_time_within_team_constrains(self):
        # given a distance object with matrix is created, team with small time constrain
        matrix = load_distances_matrix()
        distances = Distances(distances=matrix)
        vehicle = get_vehicle()
        # create team with big single journey time to comply with distance test data
        team = Team(vehicle=vehicle, time_available_sec=300, max_single_journey_time_sec=9303.673, starting_items_on_board=0) 
        
        # when validate distances for vehicle jobs in test data
        jobs = [('DOCK_328', 3), ('DOCK_210', 4), ('DOCK_60', 6), ('DOCK_267', 1)]
        start_end = ('DEPOT_1', 0)
        jobs_seq = JobsSequence(jobs=jobs, start=start_end, end=start_end)
        rs = is_journey_time_within_team_constrains(distances, jobs_seq, team)

        # then result should be true
        self.assertEqual(rs, True)

    def test_is_total_journey_time_within_team_constrains(self):

        # given a distance object with matrix is created, team with small time constrain
        matrix = load_distances_matrix()
        distances = Distances(distances=matrix)

        vehicle = get_vehicle()
        # create team with big total journey time to comply with distance test data
        team = Team(vehicle=vehicle, time_available_sec=9493.673, max_single_journey_time_sec=9303.673, starting_items_on_board=0) 
        
        # when validate distances for vehicle jobs in test data
        jobs = [('DOCK_328', 3), ('DOCK_210', 4), ('DOCK_60', 6), ('DOCK_267', 1)]
        start_end = ('DEPOT_1', 0)
        jobs_seq = JobsSequence(jobs=jobs, start=start_end, end=start_end)
        rs = is_total_journey_time_within_team_constrains(distances, jobs_seq, team)

         # then result should be true
        self.assertEqual(rs, False)

    def test_is_single_journey_time_within_team_constrains_real(self):

        # given a distance object with matrix is created, team with small time constrain
        matrix = load_distances_matrix()
        distances = Distances(distances=matrix)

        vehicle = get_vehicle()
        # create team with big total journey time to comply with distance test data
        team = Team(vehicle=vehicle, time_available_sec=25200, max_single_journey_time_sec=18000, starting_items_on_board=0) 
        
        # when validate distances for vehicle jobs in test data
        jobs = [('DOCK_101', 3), ('DOCK_280', 4), ('DOCK_399', 4), ('DOCK_301', 13), ('DOCK_155', 13)]
        start_end = ('DEPOT_1', 0)
        jobs_seq = JobsSequence(jobs=jobs, start=start_end, end=start_end)
        rs = is_single_journey_time_within_team_constrains(distances, jobs_seq, team)

         # then result should be true
        self.assertEqual(rs, True)

    def test_is_total_journey_time_outside_of_team_constrains(self):
        # given a distance object with matrix is created
        matrix = load_distances_matrix()
        team = get_team()
        distances = Distances(distances=matrix)

        # when validate distances for vehicle jobs in test data
        jobs = [('DOCK_328', 3), ('DOCK_210', 4), ('DOCK_60', 6), ('DOCK_267', 1)]
        start_end = ('DEPOT_1', 0)
        jobs_seq = JobsSequence(jobs=jobs, start=start_end, end=start_end)
        rs = is_total_journey_time_within_team_constrains(distances, jobs_seq, team)

        # then result should be True
        self.assertEqual(rs, True)

    def test_candidate_is_valid(self):
        # given a distance object with matrix is created
        matrix = load_distances_matrix()
        team = get_team()
        distances = Distances(distances=matrix)

        # when validate distances for vehicle jobs in real valid test data
        jobs = [('DOCK_280', 4), ('DOCK_399', 4), ('DOCK_110',1), ('DOCK_301', 13), ('DOCK_155', 13)]
        start_end = ('DEPOT_1', 0)
        jobs_seq = JobsSequence(jobs=jobs, start=start_end, end=start_end)
        rs = is_cadidate_valid(distances, jobs_seq, team)
        # then result should be True
        self.assertEqual(rs, True)

    def test_candidate_is_invalid(self):
        # given a distance object with matrix is created
        matrix = load_distances_matrix()
        team = get_team()
        distances = Distances(distances=matrix)

        # when validate distances for vehicle jobs in real valid test data
        jobs = [('DOCK_280', 4), ('DOCK_399', 4), ('DOCK_113',2), ('DOCK_301', 13), ('DOCK_155', 13)]
        start_end = ('DEPOT_1', 0)
        jobs_seq = JobsSequence(jobs=jobs, start=start_end, end=start_end)
        rs = is_cadidate_valid(distances, jobs_seq, team)
        # then result should be True
        self.assertEqual(rs, False)

if __name__ == '__main__':
    unittest.main()