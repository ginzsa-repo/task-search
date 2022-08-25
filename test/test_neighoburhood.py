import sys, os

import unittest

import test_utils as utils

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model import Team
from model import Solution
from model import ShiftInSameSequenceNeighbourhood
from model import SwapInSameSequenceNeighbourhood
from model import RemoveSolutionNeighbourhood
from model import InsertUnusedNeighbourhood
from model import ReplaceWithUnusedNeighbourhood


class TestNeighbourhoodCandidateGeneration(unittest.TestCase):

    # variation divided in two teams
    def expected_in_following_variations_teams(self, variations, rs):
        
        for ii, s in enumerate(rs):       
            for i, t in enumerate(s.teams):
                team_job = s.get_job_seq_at(t.id)
                if team_job.indx == i:
                    var = variations[ii][i]
                    tmp = set(var) - set(s.get_job_seq_at(t.id).jobs_seq.jobs)
                    
                    if len(tmp) != 0:
                        return False

        return True

     # variation divided in two teams
    def expected_in_oneof_following_variations_teams(self, variations, rs):
        
        for s in rs:       
            for i, t in enumerate(s.teams):
                team_job = s.get_job_seq_at(t.id)

                in_oneof =  False
                for variation in variations:
                    if team_job.indx == i:
                        var = variation[i]
                        tmp = set(var) - set(s.get_job_seq_at(t.id).jobs_seq.jobs)
                        
                        if len(tmp) == 0:
                            in_oneof = True

                if not in_oneof:
                    return False
        return True
    
    def expected_in_following_variations(self, variations, rs):   
        for sol in rs:
            for idx, team in enumerate(sol.teams):
                jbs = sol.get_job_seq_at(team.id).jobs_seq.jobs
                if jbs not in variations[idx]:
                    return False
            
        return True


    def test_shift_in_same_sequence_neighbourhood(self):
        neighbourhood = ShiftInSameSequenceNeighbourhood(1, 1.)
        all_jobs = [('DOCK_A', 3), ('DOCK_B', 4), ('DOCK_C', 6), ('DOCK_D', 1)]
        team = Team()

        solution = Solution(all_jobs, [team])
        
        for j in all_jobs:
            solution.add_job(j, team.id)

        rs = neighbourhood.generate_neighbourhood(solution, [])

        expected_variations = [[ 
                                [('DOCK_B', 4), ('DOCK_A', 3), ('DOCK_C', 6), ('DOCK_D', 1)], 
                                [('DOCK_B', 4), ('DOCK_C', 6), ('DOCK_A', 3), ('DOCK_D', 1)], 
                                [('DOCK_B', 4), ('DOCK_C', 6), ('DOCK_D', 1), ('DOCK_A', 3)], 

                                [('DOCK_A', 3), ('DOCK_C', 6), ('DOCK_B', 4), ('DOCK_D', 1)], 
                                [('DOCK_A', 3), ('DOCK_C', 6), ('DOCK_D', 1), ('DOCK_B', 4)], 
                                
                                [('DOCK_C', 6), ('DOCK_A', 3), ('DOCK_B', 4), ('DOCK_D', 1)],
                                [('DOCK_A', 3), ('DOCK_B', 4), ('DOCK_D', 1), ('DOCK_C', 6)],

                                [('DOCK_D', 1), ('DOCK_A', 3), ('DOCK_B', 4), ('DOCK_C', 6)],
                                [('DOCK_A', 3), ('DOCK_D', 1), ('DOCK_B', 4), ('DOCK_C', 6)]]]

        self.assertEqual(len(rs), 9)
        self.assertTrue(self.expected_in_following_variations(expected_variations, rs))

    def test_shift_in_same_sequence_1team_with_blocked_jobs(self):
        neighbourhood = ShiftInSameSequenceNeighbourhood(1, 1.)
        all_jobs = [('DOCK_A', 3), ('DOCK_B', 4), ('DOCK_C', 6), ('DOCK_D', 1)]
        team = Team()

        solution = Solution(all_jobs, [team])
            
        for j in all_jobs:
            solution.add_job(j, team.id)

        rs = neighbourhood.generate_neighbourhood(solution, [('DOCK_A', 3)])

        expected_variations = [[ 
                                    [('DOCK_A', 3), ('DOCK_C', 6), ('DOCK_B', 4), ('DOCK_D', 1)],
                                    [('DOCK_A', 3), ('DOCK_C', 6), ('DOCK_D', 1), ('DOCK_B', 4)], 
                                    [('DOCK_C', 6), ('DOCK_A', 3), ('DOCK_B', 4), ('DOCK_D', 1)],
                                    [('DOCK_A', 3), ('DOCK_B', 4), ('DOCK_D', 1), ('DOCK_C', 6)],
                                    [('DOCK_D', 1), ('DOCK_A', 3), ('DOCK_B', 4), ('DOCK_C', 6)],
                                    [('DOCK_A', 3), ('DOCK_D', 1), ('DOCK_B', 4), ('DOCK_C', 6)]
                                ]]

        self.assertEqual(len(rs), 6)
        self.assertTrue(self.expected_in_following_variations(expected_variations, rs))

    def test_shif_in_same_sequence_2_team(self):
        all_jobs = [('DOCK_A', 3), ('DOCK_B', 4), ('DOCK_C', 6), ('DOCK_D', 1)]
        team1 = Team()
        team2 = Team()

        solution = Solution(all_jobs, [team1, team2])
        
        # add to team 0
        solution.add_job(all_jobs[0], team1.id)
        solution.add_job(all_jobs[1], team1.id)
        # add to team 1
        solution.add_job(all_jobs[2], team2.id)
        solution.add_job(all_jobs[3], team2.id)

        neighbourhood = ShiftInSameSequenceNeighbourhood(1, 1.)
        rs = neighbourhood.generate_neighbourhood(solution, [])

        expected_variations= [
                                        [   [('DOCK_B', 4), ('DOCK_A', 3)], 
                                            [('DOCK_C', 6), ('DOCK_D', 1)]],

                                        [   [('DOCK_A', 3), ('DOCK_B', 4)], 
                                            [('DOCK_D', 1), ('DOCK_C', 6)]]
                                    ]

        self.assertEqual(len(rs), 2)

        self.assertTrue(self.expected_in_following_variations_teams(expected_variations, rs))

    def test_shif_in_same_sequence_2_team_with_blocked_jobs(self):

        all_jobs = [('DOCK_A', 3), ('DOCK_B', 4), ('DOCK_C', 6), ('DOCK_D', 1)]
        team1 = Team()
        team2 = Team()

        solution = Solution(all_jobs, [team1, team2])
        
        # add to team 0
        solution.add_job(all_jobs[0], team1.id)
        solution.add_job(all_jobs[1], team1.id)
        # add to team 1
        solution.add_job(all_jobs[2], team2.id)
        solution.add_job(all_jobs[3], team2.id)

        neighbourhood = ShiftInSameSequenceNeighbourhood(1, 1.)
        rs = neighbourhood.generate_neighbourhood(solution, [('DOCK_C', 6), ('DOCK_D', 1)])

        expected_variations= [
                                        [   [('DOCK_B', 4), ('DOCK_A', 3)], 
                                            [('DOCK_C', 6), ('DOCK_D', 1)]]
                                    ]

        self.assertEqual(len(rs), 1)
        self.assertTrue(self.expected_in_following_variations_teams(expected_variations, rs))


    # test swap
    def test_swap_in_same_sequence_one_team_real(self):
        all_jobs = [('DOCK_A', 3), ('DOCK_B', 4), ('DOCK_C', 6), ('DOCK_D', 1),  ('DOCK_E', 2)]
        team = Team()

        solution = Solution(all_jobs, [team])
        
        for j in all_jobs:
            solution.add_job(j, team.id)

        neighbourhood = SwapInSameSequenceNeighbourhood(1, 1, 1.)
        rs = neighbourhood.generate_neighbourhood(solution, [])

        expected_variations = [[ [('DOCK_A', 3), ('DOCK_B', 4), ('DOCK_C', 6), ('DOCK_E', 2), ('DOCK_D', 1)],
                                [('DOCK_A', 3), ('DOCK_B', 4), ('DOCK_D', 1), ('DOCK_C', 6), ('DOCK_E', 2)], 
                                [('DOCK_A', 3), ('DOCK_B', 4), ('DOCK_E', 2), ('DOCK_D', 1), ('DOCK_C', 6)], 
                                [('DOCK_A', 3), ('DOCK_C', 6), ('DOCK_B', 4), ('DOCK_D', 1), ('DOCK_E', 2)], 
                                [('DOCK_A', 3), ('DOCK_D', 1), ('DOCK_C', 6), ('DOCK_B', 4), ('DOCK_E', 2)], 
                                [('DOCK_A', 3), ('DOCK_E', 2), ('DOCK_C', 6), ('DOCK_D', 1), ('DOCK_B', 4)], 
                                [('DOCK_B', 4), ('DOCK_A', 3), ('DOCK_C', 6), ('DOCK_D', 1), ('DOCK_E', 2)], 
                                [('DOCK_C', 6), ('DOCK_B', 4), ('DOCK_A', 3), ('DOCK_D', 1), ('DOCK_E', 2)], 
                                [('DOCK_D', 1), ('DOCK_B', 4), ('DOCK_C', 6), ('DOCK_A', 3), ('DOCK_E', 2)], 
                                [('DOCK_E', 2), ('DOCK_B', 4), ('DOCK_C', 6), ('DOCK_D', 1), ('DOCK_A', 3)]]]

        self.assertEqual(len(rs), 10)
        self.assertTrue(self.expected_in_following_variations(expected_variations, rs))

    def test_swap_in_same_sequence_one_team_with_bloked_jobs(self):
        all_jobs = [('DOCK_A', 3), ('DOCK_B', 4), ('DOCK_C', 6), ('DOCK_D', 1)]
        team = Team()

        solution = Solution(all_jobs, [team])
        
        for j in all_jobs:
            solution.add_job(j, team.id)

        neighbourhood = SwapInSameSequenceNeighbourhood(1, 1, 1.)
        rs = neighbourhood.generate_neighbourhood(solution, [('DOCK_D', 1)])

        expected_variations = [[ [('DOCK_B', 4), ('DOCK_A', 3), ('DOCK_C', 6), ('DOCK_D', 1)], 
                                 [('DOCK_C', 6), ('DOCK_B', 4), ('DOCK_A', 3), ('DOCK_D', 1)],
                                 [('DOCK_A', 3), ('DOCK_C', 6), ('DOCK_B', 4), ('DOCK_D', 1)]]]

        self.assertEqual(len(rs), 3)
        self.assertTrue(self.expected_in_following_variations(expected_variations, rs))

    def test_swap_in_same_sequence_two_teams_real(self):
        all_jobs = [('DOCK_A', 3), ('DOCK_B', 4), ('DOCK_C', 6), ('DOCK_D', 1)]
        team1 = Team()
        team2 = Team()

        solution = Solution(all_jobs, [team1, team2])
        
        # add to team 0
        solution.add_job(all_jobs[0], team1.id)
        solution.add_job(all_jobs[1], team1.id)
        # add to team 1
        solution.add_job(all_jobs[2], team2.id)
        solution.add_job(all_jobs[3], team2.id)

        neighbourhood = SwapInSameSequenceNeighbourhood(1, 1, 1.)
        rs = neighbourhood.generate_neighbourhood(solution, [])

        expected_variations= [
                                        [   [('DOCK_B', 4), ('DOCK_A', 3)], 
                                            [('DOCK_C', 6), ('DOCK_D', 1)]],

                                        [   [('DOCK_A', 3), ('DOCK_B', 4)], 
                                            [('DOCK_D', 1), ('DOCK_C', 6)]]
                                    ]

        self.assertEqual(len(rs), 2)

        self.assertTrue(self.expected_in_following_variations_teams(expected_variations, rs)) 
    
    def test_swap_in_same_sequence_two_teams_except_one_job_real(self):

        all_jobs = [('DOCK_A', 3), ('DOCK_B', 4), ('DOCK_C', 6), ('DOCK_D', 1)]
        team1 = Team()
        team2 = Team()

        solution = Solution(all_jobs,  [team1, team2])
        
        # add to team 0
        solution.add_job(all_jobs[0], team1.id)
        solution.add_job(all_jobs[1], team1.id)
        # add to team 1
        solution.add_job(all_jobs[2], team2.id)
        solution.add_job(all_jobs[3], team2.id)

        neighbourhood = SwapInSameSequenceNeighbourhood(1, 1, 1.)
        rs = neighbourhood.generate_neighbourhood(solution, [('DOCK_D', 1)])

        expected_variations= [  [ [('DOCK_B', 4), ('DOCK_A', 3)], [('DOCK_C', 6), ('DOCK_D', 1)]] ]
                                    

        self.assertEqual(len(rs), 1)
        self.assertTrue(self.expected_in_following_variations_teams(expected_variations, rs))

    def test_removal_neighbourhood(self):
        all_jobs = [('DOCK_A', 3), ('DOCK_B', 4), ('DOCK_C', 6), ('DOCK_D', 1), ('DOCK_E', 3), ('DOCK_F', 2)]
        team1 = Team()
        team2 = Team()

        solution = Solution(all_jobs, [team1, team2])

        # add to team 0
        solution.add_job(all_jobs[0], team1.id)
        solution.add_job(all_jobs[1], team1.id)
        # add to team 1
        solution.add_job(all_jobs[2], team2.id)
        
        neighbourhood = RemoveSolutionNeighbourhood(1.)
        rs = neighbourhood.generate_neighbourhood(solution, [])
        # keep order
        expected_variations= [                
                                [   [('DOCK_A', 3),('DOCK_B', 4)],   [] ],
                                [   [('DOCK_A', 3)],                [('DOCK_C', 6)] ],
                                [   [('DOCK_B', 4)],                [('DOCK_C', 6)] ]                              
                            ]

        self.assertEqual(len(rs), 3)
        self.assertTrue(self.expected_in_oneof_following_variations_teams(expected_variations, rs))

    def test_remove_neighbourhood_with_blocked_jobs(self):
        all_jobs = [('DOCK_A', 3), ('DOCK_B', 4), ('DOCK_C', 6), ('DOCK_D', 1), ('DOCK_E', 3), ('DOCK_F', 2)]
        team1 = Team()
        team2 = Team()

        solution = Solution(all_jobs,  [team1, team2])

        # add to team 0
        solution.add_job(all_jobs[0], team1.id)
        solution.add_job(all_jobs[1], team1.id)
        # add to team 1
        solution.add_job(all_jobs[2], team2.id)

        neighbourhood = RemoveSolutionNeighbourhood(1.)
        rs = neighbourhood.generate_neighbourhood(solution, [('DOCK_C', 6)])

        # keep order
        expected_variations= [                
                                [   [('DOCK_B', 4)],                [('DOCK_C', 6)] ],
                                [   [('DOCK_A', 3)],                [('DOCK_C', 6)] ]                             
                            ]

        self.assertEqual(len(rs), 2)
        self.assertTrue(self.expected_in_oneof_following_variations_teams(expected_variations, rs))

    def test_insert_from_unfulfilled_neighbourhood(self):
        all_jobs = [('DOCK_A', 3), ('DOCK_B', 4), ('DOCK_E', 2),  ('DOCK_F', 4), ]
        team = Team()

        solution = Solution(all_jobs, [team])

         # add to team 0
        solution.add_job(all_jobs[0], team.id)
        solution.add_job(all_jobs[1], team.id)
        
        neighbourhood = InsertUnusedNeighbourhood(1.)
        rs = neighbourhood.generate_neighbourhood(solution, [])

        expected_variations = [[ [('DOCK_E', 2), ('DOCK_A', 3), ('DOCK_B', 4)],
                                 [('DOCK_A', 3), ('DOCK_E', 2), ('DOCK_B', 4)],
                                 [('DOCK_A', 3), ('DOCK_B', 4), ('DOCK_E', 2)],
                                 [('DOCK_F', 4), ('DOCK_A', 3), ('DOCK_B', 4)],
                                 [('DOCK_A', 3), ('DOCK_F', 4), ('DOCK_B', 4)],
                                 [('DOCK_A', 3), ('DOCK_B', 4), ('DOCK_F', 4)]]]

        self.assertEqual(len(rs), 6)
        self.assertTrue(self.expected_in_following_variations(expected_variations, rs))

    def test_insert_from_unfulfilled_neighbourhood_except_with_blocked_job(self):
        # unused = [('DOCK_C', 6), ('DOCK_D', 1)]
        all_jobs = [('DOCK_A', 3), ('DOCK_B', 4), ('DOCK_E', 2),  ('DOCK_F', 4)]
        team = Team()

        solution = Solution(all_jobs, [team])

         # add to team 0
        solution.add_job(all_jobs[0], team.id)
        solution.add_job(all_jobs[1], team.id)
        
        neighbourhood = InsertUnusedNeighbourhood(1.)
        rs = neighbourhood.generate_neighbourhood(solution, [('DOCK_E', 2)])

        expected_variations = [[ [('DOCK_F', 4), ('DOCK_A', 3), ('DOCK_B', 4)],
                                 [('DOCK_A', 3), ('DOCK_F', 4), ('DOCK_B', 4)],
                                 [('DOCK_A', 3), ('DOCK_B', 4), ('DOCK_F', 4)] ]]

        self.assertEqual(len(rs), 3)

    def test_replace_from_unfulfilled_neighbourhood(self):

        all_jobs = [('DOCK_A', 3), ('DOCK_B', 4), ('DOCK_E', 2),  ('DOCK_F', 4)]
        team = Team()

        solution = Solution(all_jobs, [team])

        # add to team 0
        solution.add_job(all_jobs[0], team.id)
        solution.add_job(all_jobs[1], team.id)
        
        neighbourhood = ReplaceWithUnusedNeighbourhood(1.)
        rs = neighbourhood.generate_neighbourhood(solution, [])

        expected_variations = [[[('DOCK_E', 2), ('DOCK_B', 4)],
                                [('DOCK_A', 3), ('DOCK_E', 2)],
                                [('DOCK_F', 4), ('DOCK_B', 4)],
                                [('DOCK_A', 3), ('DOCK_F', 4)]]]

        self.assertEqual(len(rs), 4)
        self.assertTrue(self.expected_in_following_variations(expected_variations, rs))

    def test_replace_from_unfulfilled_neighbourhood_with_blocked_jobs(self):
        all_jobs = [('DOCK_A', 3), ('DOCK_B', 4), ('DOCK_E', 2),  ('DOCK_F', 4)]
        team = Team()

        solution = Solution(all_jobs,  [team])

        # add to team 0
        solution.add_job(all_jobs[0], team.id)
        solution.add_job(all_jobs[1], team.id)

        neighbourhood = ReplaceWithUnusedNeighbourhood(1.)
        rs = neighbourhood.generate_neighbourhood(solution, [('DOCK_E', 2), ('DOCK_A', 3)])

        expected_variations = [[[('DOCK_A', 3), ('DOCK_F', 4)]]]
            
        self.assertEqual(len(rs), 1)
        self.assertTrue(self.expected_in_following_variations(expected_variations, rs))

if __name__ == '__main__':
    unittest.main()
