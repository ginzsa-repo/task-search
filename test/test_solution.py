import sys, os

import unittest

import test_utils as utils

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model import Team
from model import Solution
from model import JobsSequence


class TestSolution(unittest.TestCase):

    '''
    Test construct Solution object

    '''
    def test_solution_constructor(self):

        # given the following jobs for one team
        all_jobs = [('DOCK_A', 3), ('DOCK_B', 4), ('DOCK_C', 6), ('DOCK_D', 1)]
        team = Team()
        teams = [team]

        # when a solution is constructed
        solution = Solution(all_jobs, teams)

        # then the solution should have the jobs as anfulfilled, one team, no jobs in sequence
        self.assertEqual(len(solution.unfulfilled), 4)
        self.assertEqual(len(solution.team_jobs), 1)
        self.assertEqual(len(solution.get_job_seq_at(0).jobs_seq.jobs), 0)


    '''
    Test construct Solution object and add the jobs

    '''
    def test_solution_add_jobs(self):
        # given the following jobs for one team
        all_jobs = [('DOCK_A', 3), ('DOCK_B', 4), ('DOCK_C', 6), ('DOCK_D', 1)]
        team = Team()
        teams = [team]

         # when a solution is constructed and all jobs are added
        solution = Solution(all_jobs, teams)
        
        for j in all_jobs:
            solution.add_job(j,0)

        # then the solution should NOT have jobs as anfulfilled, one team and ALL jobs in sequence
        self.assertEqual(len(solution.get_job_seq_at(0).jobs_seq.jobs), 4)
        self.assertEqual(len(solution.unfulfilled), 0)


    def test_job_seq_construction(self):

        # given the following jobs for one team
        all_jobs = [('DOCK_A', 3), ('DOCK_B', 4), ('DOCK_C', 6), ('DOCK_D', 1)]
        team = Team()
        teams = [team]

         # when a solution is constructed and all jobs are added
        solution = Solution(all_jobs, teams)
        
        for j in all_jobs:
            solution.add_job(j,0)

        # and when copy jobs sequence from given solution 
        post = [('DOCK_A', 3), ('DOCK_B', 4), ('DOCK_C', 6), ('DOCK_D', 1), ('DOCK_F', 2)]
        str = solution.team_jobs[0].jobs_seq.start
        end = solution.team_jobs[0].jobs_seq.end

        post_job_seq = JobsSequence(jobs=post, start=str, end=end)

        # then job sequence's start and end content should be the same as solution
        # and jobs should hold the extra new job
        self.assertEqual(post_job_seq.jobs, post)
        self.assertEqual(post_job_seq.start, str)
        self.assertEqual(post_job_seq.end, end)

if __name__ == '__main__':
    unittest.main()
