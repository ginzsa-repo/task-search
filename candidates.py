import logging
import sys
from validation import is_cadidate_valid
from fitness import job_fitness
from utils import clone_pre_post_jobs, clone_pre_post_to_jobs
from model import JobsSequence
from model import Candidate

logger = logging.getLogger()

'''
create candidate list from solution
'''
def create_canditate_list(config, distances, best_solution):

    logger.info('creating initial candidate list ...')
    candidate_store = CandidateStore(config=config, distances=distances)
    candidate_store.create_list(best_solution)
    return candidate_store
    
'''
get best candidate
'''
def sort_get_best_candidate(candidate_store):
    candidate_store.all_candidates.sort(key=lambda x: x.fitness, reverse=True)
    return candidate_store.all_candidates[0]

'''
apply candidate to solution
'''
def apply_candidate(solution, candidate):
    # [team_idx,  idx, j[0], j[1], fitness]
    solution.add_job(candidate.job, candidate.team.id, job_seq_idx=candidate.position)

'''
update candidates store for each iteration
'''
def update_candidates_store_for_solution(candidates_store, team, to_solution):

    # if still have candidates
    while candidates_store.size() > 0:
        # pick and remove best "move" candidate (peek from top)
        candidate = sort_get_best_candidate(candidates_store)
        logger.info('candidate: {}'.format(candidate.candidate))
        if candidate is not None:
            apply_candidate(to_solution, candidate)
            logger.debug('solution candidates ... {}'.format(to_solution.team_jobs_map[team.id].jobs_seq.jobs))

            # extract  more candidates with the new addition
            candidates_store.remove_candidate(candidate)
            candidates_store.create_candidates_for_team(to_solution.unfulfilled, to_solution.team_jobs_map[team.id])
    
    logger.debug('... end candidate creation')
   
def build_solution_candidate(candidate_store, best_solution):

    logger.info('building solution with candidates ... {}'.format(candidate_store.size()))
    for team in best_solution.teams:
        logger.info('extract candidate for solution for team:{} vehicle: {}'.format(team.id, team.vehicle))
        update_candidates_store_for_solution(candidate_store, team, best_solution)
 
'''
jobs is list of tuples: location id and a value representing a specific number of items (for a job) 
in our example docking station id and number of broken bikes ' ('DOCK_0', 0) '
'''
class CandidateStore:
    def __init__(self, *args, **kwargs):
        self.all_candidates = []
        self.candidates_by_team = {}
        self.candidates_by_job = {}
        self.candidate_holders = {}

        self.config = kwargs.get('config', None)
        self.distances = kwargs.get('distances', None)

    def create_list(self, solution):
        for t in solution.teams:
            self.candidates_by_team[t] = []

        for tj in list(solution.team_jobs_map.values()):
            self.create_candidates_for_team(solution.unfulfilled, tj)


    def create_candidates_for_team(self, unfullfilled, team_jobs):

        for j in unfullfilled.items():
            team = team_jobs.team
            job_seq =  team_jobs.jobs_seq
             # put jobs in different index positions in the job sequence
            for position in range(0, len(job_seq.jobs) + 1):
                post = clone_pre_post_to_jobs(position, job_seq.jobs, j)
                # post addition job sequence
                post_job_seq = JobsSequence(jobs=post, start=job_seq.start, end=job_seq.end, team=team)
                # comply with validations : 
                if is_cadidate_valid(self.distances, post_job_seq, team):
                    # calculate fitness
                    logger.debug('team job sequence size: {}'.format(len(post_job_seq.jobs)))
                    fitness = (job_fitness(self.config, self.distances, post_job_seq, team) - job_fitness(self.config, self.distances, job_seq, team))
                    if fitness != -sys.float_info.max:
                        self.add_candidate(Candidate(candidate=[team,  position, j[0], j[1], fitness]))

                else:
                    logger.debug('temp job not valid: {}'.format(j))
                    
                    
    def add_candidate(self, candidate):
        self.all_candidates.append(candidate)
        candidate_job_map = self.candidates_by_job.get(candidate.job_key)
        if candidate_job_map is None:
            candidate_job_map = set()
            self.candidates_by_job[candidate.job_key] = candidate_job_map
        candidate_job_map.add(candidate)
            

        candidate_team_map = self.candidates_by_team.get(candidate.team.id)
        if candidate_team_map is None:
            candidate_team_map = set()
            self.candidates_by_team[candidate.team.id] = candidate_team_map
        candidate_team_map.add(candidate)

        holders = self.candidate_holders.get(candidate.id, [])
        holders.append(self.all_candidates)
        holders.append(candidate_job_map)
        holders.append(candidate_team_map)
        self.candidate_holders[candidate.id] = holders

    def remove_candidate(self, candidate):
        candidate_jobs_map = self.candidates_by_job.get(candidate.job_key)
        if candidate_jobs_map is not None:
            for cand in candidate_jobs_map.copy():
                self.remove_from_all_containers(cand)

        candidate_team_map = self.candidates_by_team.get(candidate.team.id)
        if candidate_team_map is not None:
            for cand in candidate_team_map.copy():
                self.remove_from_all_containers(cand)
               
    def remove_from_all_containers(self, candidate):
        for holder in self.candidate_holders.get(candidate.id, []):
            if candidate in holder:
                holder.remove(candidate)
        if candidate.id in self.candidate_holders:
            del self.candidate_holders[candidate.id]

        logger.debug('all candidate size: {}'.format(len(self.all_candidates)))

    def size(self):
        return len(self.all_candidates)
        



    




