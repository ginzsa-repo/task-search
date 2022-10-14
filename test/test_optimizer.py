import sys, os
import unittest
import json

# keep this as an example
'''
GRAPHQL EXAMPLE

{
  DistanceMatrix(where:{spId1:{_in:["DEPOT_1", "DEPOT_2"]}}) {
    distance
    spId1
    spId2
  }
}
'''


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import utils
from model import Team
from model import Vehicle
from optimizer import Optimizer
from distances import Distances

class TestOptimizer(unittest.TestCase):

    def test_optimizer_load_test_data(self):
        jobs, _ = load_broken_items()
        self.assertTrue(jobs is not None)
        self.assertTrue(len(jobs) > 0)
        self.assertTrue(type(jobs[0]) == tuple) 

        matrix = load_distances_matrix()
        self.assertTrue(matrix is not None)

    def test_optimizer_construction(self):
        # given we create an optimizer (wtih test data)
        optimizer = create_optimizer()

        # when retrieve its component
        jbs = optimizer.jobs
        mtx = optimizer.distances
        tms = optimizer.teams
        cnf = optimizer.config
        dps = optimizer.depos

        # then optimizer is not None and has all its components
        self.assertTrue(optimizer is not None)

        self.assertTrue(jbs is not None)
        self.assertTrue(len(jbs) > 0)

        self.assertTrue(mtx is not None)
        self.assertTrue(type(mtx) is Distances)

        self.assertTrue(cnf is not None)
        self.assertTrue(type(cnf) is dict)

        self.assertTrue(tms is not None)
        self.assertTrue(len(tms) == 1)

        self.assertTrue(dps is not None)
        self.assertTrue(len(dps) > 0)


    def test_optimizer_run(self):
        # given we create an optimizer (wtih test data)
        optimizer = create_optimizer()

        # when optimize method is called
        rs = optimizer.optimize()

        # then result should be not None
        self.assertTrue(rs)

        for team in rs['solution'].teams:
            print('team: ', team.id)
            jseq = rs['solution'].get_job_seq_at(team.id)
            print('jobs seq: ', jseq.jobs_seq)
        print(rs)

def create_optimizer():
    jobs, depos = load_broken_items()
    matrix = load_distances_matrix()
    config = {'tabu_size': 4, 'iterations': 10, 'item_weight':10_000, 'time_weight': 1}
    teams = [get_team()]

    return Optimizer(jobs=jobs, matrix=matrix, config=config, teams=teams, depos=depos)

def load_broken_items():
    
    test_data_location = './test/data/ba/lockedinbikes-2019-08-28--23-00.json'
    with open(test_data_location) as json_file:
        data = json.load(json_file) 

    jobs = []
    assumed_depo = []
    for item in data:
        if there_is_a_job(item['numitems']):
            jobs.append((item['servicePointId'], item['numitems']))
        else:
            assumed_depo.append((item['servicePointId'], item['numitems']))
    return jobs, assumed_depo

'''
Assuming that there is a job where there is items to collect
'''
def there_is_a_job(number_of_items):
    return number_of_items > 0

def load_distances_matrix():
    test_data_distance = './test/data/ba/distances.json'
    # map original data headers into service's header names 
    distance_mapper = {'origin': 'originSpId', 'destination':'destinationSpId', 'items_path': 'spDMResult/items'}
    matrix = utils.create_distance_matrix_from_json_file_mapper(distance_mapper, test_data_distance)
    return matrix

def get_vehicle():
   return Vehicle(capacity=23, avg_load_time_sec=60, avg_stopping_time_sec=300)

def get_team():
   test_vehicle = get_vehicle()
   return Team(vehicle=test_vehicle, time_available_sec=25200, max_single_journey_time_sec=18000, starting_items_on_board=0) 
   
if __name__ == '__main__':
    unittest.main()
