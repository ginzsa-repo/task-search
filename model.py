import logging
import copy
from operator import truediv
import uuid
import random
from bidict import bidict

logger = logging.getLogger()

class Vehicle:
    def __init__(self, *args, **kwargs):
        self.capacity = kwargs.get('capacity', None)
        self.avg_load_time_sec = kwargs.get('avg_load_time_sec', None)
        self.avg_stopping_time_sec = kwargs.get('avg_stopping_time_sec', None)
        self.speed = kwargs.get('speed', 15.) # default to 15
        self.id = str(uuid.uuid4())

class Team:
    def __init__(self, *args, **kwargs):
        self.vehicle = kwargs.get('vehicle', None)
        self.time_available_sec = kwargs.get('time_available_sec', None) 
        self.max_single_journey_time_sec = kwargs.get('max_single_journey_time_sec', None) 
        self.starting_bikes_on_board = kwargs.get('starting_bikes_on_board', None) 
        self.allowed_end_depot = ['DEPOT_1']
        self.id = str(uuid.uuid4())
        self.start_depo = kwargs.get('start_depo', self.allowed_end_depot[0])

'''
job sequence contain a list 'sequence' of touple ('DOCK_2',3) jobs
it also contain the start and end ds
'''
class JobsSequence:

    def __init__(self, *args, **kwargs):
        self.team = kwargs.get('team')
        jobs_seq = kwargs.get('jobs_seq', None)
        if jobs_seq is None:
            self.jobs = kwargs.get('jobs', [])
            self.start = kwargs.get('start', (self.team.start_depo, 0))
            self.end = kwargs.get('end', (self.team.start_depo, 0))
        else:
            self.jobs.append(jobs_seq.jobs)
            self.start = jobs_seq.start
            self.end = jobs_seq.end

'''
Team jobs, job sequence  and teams
'''
class TeamJobs:
    def __init__(self, *args, **kwargs):
        self.team = kwargs.get('team', None)
        self.indx = kwargs.get('indx', None)

        self.jobs_seq = None
        jbs_seq = kwargs.get('jobs_seq', None)

        if jbs_seq is None:
            self.jobs_seq = JobsSequence(team=self.team)
        else:
            self.jobs_seq = JobsSequence(jobs_seq=jbs_seq, team=self.team)

'''
jobs is list of dock id, no of broken bikes touples ' ('DOCK_0', 0) '
'''
class Solution:
    def __init__(self, jobs, teams):
        self.teams = teams

        if type(jobs) == dict: # for clone
            self.unfulfilled = jobs
        else:
            self.unfulfilled = dict((j[0], j[1]) for j in jobs)

        self.team_jobs_map = {}
        self.affected_jobs = []
        for i, t in enumerate(teams):
            tj = TeamJobs(team=t, indx=i)
            self.team_jobs_map[t.id] = tj
        self.id = str(uuid.uuid4())

    '''
    when a job is added, should be removed from the 'unfulfilled', 
    '''
    def add_job(self, job_in, idx, job_seq_idx=None):
        logger.debug('adding job {}'.format(job_in))
        job_in_tuple = None 

        if type(job_in) == tuple:
            job_in_tuple = job_in
            job_in = job_in[0]

        # get obj from dict and delete
        j = self.unfulfilled.get(job_in, None)

        logger.debug('job: ({},{}) with unfullfiled size: {}'.format(job_in, j, len(self.unfulfilled)))

        # if is in unfulfilled, delete it
        if j is not None:
            del self.unfulfilled[job_in]
            job_to_append =(job_in, j)
        else:
            job_to_append = job_in_tuple

        logger.debug('job extracted: {} with unfulfilled size: {}'.format(job_to_append, len(self.unfulfilled)))

        if job_seq_idx is None:    
            self.team_jobs_map[idx].jobs_seq.jobs.append(job_to_append)
        else:
            self.team_jobs_map[idx].jobs_seq.jobs.insert(job_seq_idx, job_to_append)

    def get_job_seq_at(self, idx):
        return self.team_jobs_map[idx]

    def clone(self):
        cloned_solution = Solution(copy.deepcopy(self.unfulfilled), copy.deepcopy(self.teams))
        # copy the same job values from other team different to idx
        for team in self.teams:
            in_jobs = self.get_job_seq_at(team.id).jobs_seq.jobs
            for idx, in_job in enumerate(in_jobs):
                cloned_solution.add_job(in_job, team.id, job_seq_idx=idx)
                
        return cloned_solution

    def collect_all_jobs(self):
        all_jobs = []
        for team in self.teams:
            in_jobs = self.get_job_seq_at(team.id).jobs_seq.jobs
            all_jobs.append(in_jobs)
        return all_jobs


'''
Candidate 
[team_jobs.indx,  idx, j[0], j[1], fitness]
'''
class Candidate:
    def __init__(self, *args, **kwargs):
        self.candidate = kwargs.get('candidate')
        if self.candidate is None:
            self.team = kwargs.get('team')
            self.position = kwargs.get('pos')
            self.item = kwargs.get('item')
            self.value = kwargs.get('value')
            self.fitness = kwargs.get('fitness')
            self.candidate = [self.team.id, self.position, self.item, self.value, self.fitness]
        else:
            self.team = self.candidate[0]
            self.position = self.candidate[1]
            self.item = self.candidate[2]
            self.value = self.candidate[3]
            self.fitness = self.candidate[4]
        
        self.job_key =  '{}-{}'.format(self.item, self.value)
        self.job = (self.item, self.value)
        self.id = str(uuid.uuid4())


'''
neighbourhood clasess
'''
# shift neighbourhood
class ShiftInSameSequenceNeighbourhood:
    def __init__(self, width, sample_freq):
        self.width = width
        self.sample_freq = sample_freq
        self.id = str(uuid.uuid4())
        self.intra_route_mover = IntraRouterMover()

    '''
    generate neighbourhood
    '''
    def generate_neighbourhood(self, solution, jobs_to_ignore):
        random.seed(0)
        solutions = []
        split_points = AllowedConsecutiveSplitPointCreator(solution, jobs_to_ignore, self.width)
        filtered_unfulfilled = self.create_filtered_unfulfilled(solution, jobs_to_ignore)
        for team in solution.teams:
            team_jobs = solution.get_job_seq_at(team.id)
            for seq in split_points.split_point_map[team.id]:
                start_a = seq[0]
                end_excl = seq[-1] + 1
                for start_b in range(0, len(team_jobs.jobs_seq.jobs)):
                    if self.overlap(start_a, start_b):
                        continue
                    if self.symmetry(start_a, start_b):
                        continue
                    if random.uniform(0, 1.0) >= self.sample_freq:
                        continue

                    new_solution = self.generate_solution(solution, filtered_unfulfilled, team.id, start_a, end_excl, start_b)
                    solutions.append(new_solution)

        return solutions

    def generate_solution(self, solution, filtered_unfulfilled, team_id, start_a, end_excl, start_b):
        new_solution = solution.clone()
        new_solution.unfulfilled = filtered_unfulfilled
        team_jobs = new_solution.get_job_seq_at(team_id)
        affected = self.intra_route_mover.move_sub_sequence(team_jobs.jobs_seq.jobs, start_a, end_excl, start_b)
        new_solution.affected_jobs =  new_solution.affected_jobs + list(affected)
        return new_solution
    

    def create_filtered_unfulfilled(self, solution, jobs_to_ignore):
        unfulfilled_copy = copy.deepcopy(solution.unfulfilled)
        for j in jobs_to_ignore:
            if j[0] in unfulfilled_copy:
                del unfulfilled_copy[j[0]]
        return unfulfilled_copy

    def overlap(self, start_a, start_b):
        if start_b >= start_a and start_b < (start_a + self.width):
            return True
        return False

    def symmetry(self, start_a, start_b):
        if start_b == start_a - self.width:
            return True
        return False
    
    def __repr__(self):
        return f"{self.__class__.__name__}(width={self.width}, freq={self.sample_freq})"
            

class AllowedConsecutiveSplitPointCreator:
    def __init__(self, solution, jobs_to_ignore, consecutive_point_width):
        self.map_team = bidict({})
        self.split_point_map = {}
        for idx, team in enumerate(solution.teams):
            self.map_team[idx] = team
            self.split_point_map[team.id] = []
            team_jobs = solution.get_job_seq_at(team.id)
            jobs = team_jobs.jobs_seq.jobs
            self.create_and_add_split_points_for_team(team, jobs, jobs_to_ignore, consecutive_point_width)

    def create_and_add_split_points_for_team(self, team, jobs, jobs_to_ignore, consecutive_point_width):

        for idx in range(0, (len(jobs) - consecutive_point_width) + 1):
            try:
                sequence = self.create_valid_sequence(jobs, jobs_to_ignore, consecutive_point_width, idx)
                self.split_point_map.get(team.id).append(sequence)
            except Exception as ex:
                logger.debug(ex.args)
                continue

    def create_valid_sequence(self, jobs, jobs_to_ignore, consecutive_point_width, i):
        sequence = []
        for j in range(i, (i + consecutive_point_width)):
            if jobs[i] in jobs_to_ignore:
                raise Exception (i, jobs[i])
            else:
                 sequence.append(j)
        return sequence


class IntraRouterMover:
    def __init__(self):
        self.id = str(uuid.uuid4())
    '''
    Moves subsequence within the same sequence
    '''
    def move_sub_sequence(self, jobs, start_a, end_a, start_b):
        affected = set()
        if start_b >= start_a:
            for i in range(0, (end_a - start_a)):
                job = jobs.pop(start_a)        
                jobs.insert(start_b, job)
                affected.add(job)
        else:
            for i in range(0, (end_a - start_a)):
                job = jobs.pop(start_a + i)        
                jobs.insert(start_b + i, job)
                affected.add(job)

        return affected
    '''
    Swaps sub-sequences of the same sequence
    '''
    def swap_sub_sequence(self, jobs, start_a, end_a, start_b, end_b):
        width_a = end_a - start_a
        width_b = end_b - start_b
        affected = set()

        if start_a < start_b:
            for i in range(0, width_b):
                job = jobs.pop(start_b + i)        
                jobs.insert(start_a + i, job)
                affected.add(job)
            insert_point = start_b - 1 + width_b
            for i in  range(0, width_a):
                job = jobs.pop(start_a + width_b)
                jobs.insert(insert_point, job)
                affected.add(job)
        else:
            for i in range(0, width_a):
                job = jobs.pop(start_a + i)
                jobs.insert(start_b + i, job)
                affected.add(job)
            insert_point =  start_a - 1 + width_a
            for i in range(0, width_b):
                job = jobs.pop(start_b + width_a)
                jobs.insert(insert_point, job)
                affected.add(job)
        return affected

# swap neighbourhood
class SwapInSameSequenceNeighbourhood:
    def __init__(self, widtha, widthb, sample_freq):
        self.width_a = widtha
        self.width_b = widthb
        self.sample_freq = sample_freq
        self.intra_route_mover = IntraRouterMover()
        self.id = str(uuid.uuid4())

    '''
    generate neighbourhood
    '''
    def generate_neighbourhood(self, solution, jobs_to_ignore):
        random.seed(0)
        solutions = []
        split_points_a = AllowedConsecutiveSplitPointCreator(solution, jobs_to_ignore, self.width_a)
        split_points_b = AllowedConsecutiveSplitPointCreator(solution, jobs_to_ignore, self.width_b)
        filtered_unfulfilled = self.create_filtered_unfulfilled(solution, jobs_to_ignore)

        for team in solution.teams:
            team_jobs = solution.get_job_seq_at(team.id)
            for seq_a in split_points_a.split_point_map[team.id]:
                start_a = seq_a[0]
                end_a = start_a + self.width_a

                for seq_b in split_points_b.split_point_map[team.id]:
                    start_b = seq_b[0]
                    end_b = start_b + self.width_b

                    if self.overlap(start_a, start_b):
                        continue
                    if self.symmetry(start_a, start_b):
                        continue
                    if random.uniform(0, 1.0) >= self.sample_freq:
                        continue

                    new_solution = self.generate_solution(solution, filtered_unfulfilled, team.id, start_a, end_b, start_b, end_b)
                    solutions.append(new_solution)

        return solutions

    def generate_solution(self, solution, filtered_unfulfilled, team_id, starta, enda, startb, endb):
        new_solution = solution.clone()
        new_solution.unfulfilled = filtered_unfulfilled
        team_jobs = new_solution.get_job_seq_at(team_id)
        affected = self.intra_route_mover.swap_sub_sequence(team_jobs.jobs_seq.jobs, starta, enda, startb, endb)
        new_solution.affected_jobs =  new_solution.affected_jobs + list(affected)
        return new_solution
    

    def create_filtered_unfulfilled(self, solution, jobs_to_ignore):
        unfulfilled_copy = copy.deepcopy(solution.unfulfilled)
        for j in jobs_to_ignore:
            if j[0] in unfulfilled_copy:
                del unfulfilled_copy[j[0]]
        return unfulfilled_copy

    def overlap(self, start_a, start_b):
        if start_a >= start_b and start_a < (start_b + self.width_b):
            return True

        if start_b >= start_a and start_b < (start_a + self.width_a):
            return True
        return False

    def symmetry(self, start_a, start_b):
        if self.width_a == self.width_b:
            if start_a > start_b:
                return True
        return False
    
    def __repr__(self):
        return f"{self.__class__.__name__}(width_a={self.width_a}, width_b={self.width_b}, freq={self.sample_freq})"

# remove neighbours
class RemoveSolutionNeighbourhood:
    def __init__(self, sample_freq):
        self.sample_freq = sample_freq
        self.id = str(uuid.uuid4())
        self.intra_route_mover = IntraRouterMover()
    '''
    generate neighbourhood
    ''' 
    def generate_neighbourhood(self, solution, jobs_to_ignore):
        random.seed(0)
        solutions = []
        split_points = AllowedConsecutiveSplitPointCreator(solution, jobs_to_ignore, 1)
        filtered_unfulfilled = self.create_filtered_unfulfilled(solution, jobs_to_ignore)
        for team in solution.teams:
            team_jobs = solution.get_job_seq_at(team.id)
            for seq in split_points.split_point_map[team.id]:
                if random.uniform(0, 1.0) >= self.sample_freq:
                    continue
                
                new_solution = self.generate_solution(solution, filtered_unfulfilled, team.id, seq)
                solutions.append(new_solution)
        return solutions

    def generate_solution(self, solution, filtered_unfulfilled, team_id, removal_seq):
        new_solution = solution.clone()
        new_solution.unfulfilled = filtered_unfulfilled
        team_jobs = new_solution.get_job_seq_at(team_id)
        for to_remove in removal_seq:
            job = team_jobs.jobs_seq.jobs.pop(to_remove)
            new_solution.affected_jobs.append(job)
        return new_solution

    def create_filtered_unfulfilled(self, solution, jobs_to_ignore):
        unfulfilled_copy = copy.deepcopy(solution.unfulfilled)
        for j in jobs_to_ignore:
            if j[0] in unfulfilled_copy:
                del unfulfilled_copy[j[0]]
        return unfulfilled_copy
    
    def __repr__(self):
        return f"{self.__class__.__name__}(freq={self.sample_freq})"
                
# insert neighbour
class InsertUnusedNeighbourhood:
    def __init__(self, sample_freq):
        self.sample_freq = sample_freq
        self.id = str(uuid.uuid4())
    
    '''
    generate neighbourhood
    ''' 
    def generate_neighbourhood(self, solution, jobs_to_ignore):
        random.seed(0)
        solutions = []
        filtered_unfulfilled = self.create_filtered_unfulfilled(solution, jobs_to_ignore)
        for key in filtered_unfulfilled:
            job = (key, filtered_unfulfilled[key])
            for team in solution.teams:
                team_jobs = solution.get_job_seq_at(team.id)
                for i in range(0, len(team_jobs.jobs_seq.jobs) + 1):
                    if random.uniform(0, 1.0) >= self.sample_freq:
                        continue
                    new_solution = self.generate_solution(solution, filtered_unfulfilled, team.id, job, i)
                    solutions.append(new_solution)
        return solutions

    def create_filtered_unfulfilled(self, solution, jobs_to_ignore):
        unfulfilled_copy = copy.deepcopy(solution.unfulfilled)
        for j in jobs_to_ignore:
            if j[0] in unfulfilled_copy:
                del unfulfilled_copy[j[0]]
        return unfulfilled_copy

    def generate_solution(self, solution, filtered_unfulfilled, team_id, job, idx):
        new_solution = solution.clone()
        new_solution.unfulfilled = filtered_unfulfilled
        team_jobs = new_solution.get_job_seq_at(team_id)
        team_jobs.jobs_seq.jobs.insert(idx, job)
        new_solution.affected_jobs.append(job)
        return new_solution

    def __repr__(self):
        return f"{self.__class__.__name__}(freq={self.sample_freq})"

# replace
class ReplaceWithUnusedNeighbourhood:
    def __init__(self, sample_freq):
        self.sample_freq = sample_freq
        self.id = str(uuid.uuid4())
    
    '''
    generate neighbourhood
    ''' 
    def generate_neighbourhood(self, solution, jobs_to_ignore):
        random.seed(0)
        solutions = []
        filtered_unfulfilled = self.create_filtered_unfulfilled(solution, jobs_to_ignore)
        split_points = AllowedConsecutiveSplitPointCreator(solution, jobs_to_ignore, 1)

        for key in filtered_unfulfilled:
            job = (key, filtered_unfulfilled[key])
            for team in solution.teams:
                team_jobs = solution.get_job_seq_at(team.id)
                for seq in split_points.split_point_map[team.id]:
                    if len(seq) == 0:
                        continue
                    if random.uniform(0, 1.0) >= self.sample_freq:
                        continue  
                    new_solution = self.generate_solution(solution, filtered_unfulfilled, team.id, job, seq)
                    solutions.append(new_solution)
        return solutions

    def create_filtered_unfulfilled(self, solution, jobs_to_ignore):
        unfulfilled_copy = copy.deepcopy(solution.unfulfilled)
        for j in jobs_to_ignore:
            if j[0] in unfulfilled_copy:
                del unfulfilled_copy[j[0]]
        return unfulfilled_copy

    def generate_solution(self, solution, filtered_unfulfilled, team_id, job, seq):
        new_solution = solution.clone()
        new_solution.unfulfilled = filtered_unfulfilled
        team_jobs = new_solution.get_job_seq_at(team_id)
        new_solution.affected_jobs.append(job)
        for i in seq:
            ijob =  team_jobs.jobs_seq.jobs.pop(i)
            new_solution.affected_jobs.append(ijob)

        team_jobs.jobs_seq.jobs.insert(seq[0], job)

        return new_solution
    
    def __repr__(self):
        return f"{self.__class__.__name__}(freq={self.sample_freq})"
