import sys, os

import json
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model import Team
from model import Solution
import utils


test_data_location = './test/data/ba/lockedinbikes-2019-08-28--23-00.json'
test_data_distance = './test/data/ba/distances.json'

class TestUtils(unittest.TestCase):
  '''
  testing loading the test data
  '''
  def test_load_data(self):
    data = utils.load_test_data(test_data_distance)

    self.assertTrue(data is not None)
    self.assertTrue(data['spDMResult'] is not None)

  '''
    get matrix from json file (buenos aires example)
    matrix should look like:
    matrix[from][to] : item(from, to, distance, vehicle, href)
  '''
  def test_create_distance_matrix_from_json_file(self):
    distances = utils.create_distance_matrix_from_json_file(test_data_distance)
    self.assertTrue(distances is not None)
    self.assertTrue(len(distances.keys()) > 0)

    for frm in distances.keys():     
      for to in distances[frm].keys():
        item = distances[frm][to]
        self.assertEqual(item['originSpId'], frm)
        self.assertEqual(item['destinationSpId'], to)


  def test_create_distance_matrix_from_json_file_use_mapping(self):
    distance_mapper = {'origin': 'originSpId', 'destination':'destinationSpId', 'items_path': 'spDMResult/items'}
    distances = utils.create_distance_matrix_from_json_file_mapper(distance_mapper, test_data_distance)
    self.assertTrue(distances is not None)
    self.assertTrue(len(distances.keys()) > 0)

    for frm in distances.keys():     
      for to in distances[frm].keys():
        item = distances[frm][to]
        self.assertEqual(item['originSpId'], frm)
        self.assertEqual(item['destinationSpId'], to)


  def test_clone_pre_post_to_jobs(self):
    # given this jobs and new job to add
    all_jobs = [('DOCK_A', 3), ('DOCK_B', 4), ('DOCK_C', 6), ('DOCK_D', 1)]
    new_job = ('DOCK_F', 1)

    # when jobs pre and post addition are cloned
    post = utils.clone_pre_post_to_jobs(4, all_jobs, new_job)

    # then post should include the job added
    self.assertEqual(len(post), 5)
    self.assertTrue(post[4] == new_job)


  def test_clone_pre_post_to_jobs_from_solution(self):
    # given the following jobs for one team and a new job
    all_jobs = [('DOCK_A', 3), ('DOCK_B', 4), ('DOCK_C', 6), ('DOCK_D', 1)]
    new_job = ('DOCK_F', 1)

    team = Team()
    teams = [team]

    # when a solution is constructed and all jobs are added
    solution = Solution(all_jobs, teams)
        
    for j in all_jobs:
      solution.add_job(j,team.id)

    # and when jobs pre and post addition are cloned from given solution
    post = utils.clone_pre_post_jobs(solution, 4, new_job, team.id)

    # then pre should hold the same jobs as all jobs and post should include the job added
    self.assertEqual(len(post), 5)
    self.assertTrue(post[4] == new_job)
      

  def test_path_navigate_to_object(self):
    # given the following dict
    result_value = 3
    a = {'a':'1', 'b': {'c':'2','d':{'f':result_value}}}

    # when a path navigation to b/d/f'
    rs = utils.path_navigate_to_object(a, 'b/d/f')

    # then rs should be result_value
    self.assertTrue(rs == result_value)


if __name__ == '__main__':
    unittest.main()

