
from utils import clone_pre_post_jobs
from travel_calculator import total_travel_time_in_sec, sum_no_items_except_last_job, calculate_total_time_in_seconds, max_single_travel_time_in_sec
import logging

logger = logging.getLogger()
'''
validate that distances are present for all jobs
'''
def is_distance_valid_for_vehicle(distances, solution):

    for team in solution.teams:
        jobs_seq = solution.get_job_seq_at(team.id).jobs_seq
        valid = is_distance_valid_for_job_vehicle(distances, jobs_seq, team)
        if not valid:
            return False

    return True

def is_distance_valid_for_job_vehicle(distances, jobs_seq, team):

    previous_job = None
    jobs_to_validate = jobs_seq.jobs
    if jobs_seq.start is not None:
        jobs_to_validate = [jobs_seq.start] + jobs_to_validate
    
    if jobs_seq.end is not None:
        jobs_to_validate = jobs_to_validate + [jobs_seq.end]

    for job in jobs_to_validate:
        if previous_job is not None:
            # if station data is not in distance travel matrix return False
            if distances.get_travel_time(previous_job, job, team.vehicle.speed) == -1:
                return False
        previous_job = job

    return True


'''
validates if is within vahicle's load capacity constrains
'''
def is_journey_capacity_within_constrains(solution):
    for team in solution.teams:
        jobs_seq = solution.get_job_seq_at(team.id).jobs_seq
        valid = is_journey_capacity_within_vehicle_constrain(jobs_seq, team.vehicle)
        if not valid:
            return False

    return True

def is_journey_capacity_within_vehicle_constrain(jobs, vehicle):
    no_items_so_far = sum_no_items_except_last_job(jobs)
    logger.debug('no of items so far {}, vehicle capacity: {}'.format(no_items_so_far, vehicle.capacity))
    return  no_items_so_far <= vehicle.capacity
    
'''
validates that jorney's time is within the team's vehicle time constrains
'''
def is_journey_time_within_constrains(distances, solution):
    for team in solution.teams:

        jobs_seq = solution.get_job_seq_at(team.id)
        valid = is_journey_time_within_team_constrains(distances, jobs_seq, team)

        if not valid:
            return False

    return True

def is_journey_time_within_team_constrains(distances, jobs, team):
    total_travel_time = total_travel_time_in_sec(distances, jobs, team)
    logger.debug('total travel time in sec {}, max team single journey: {}'.format(total_travel_time, team.max_single_journey_time_sec))
    return total_travel_time < team.max_single_journey_time_sec

'''
is a single max journey withing team constrains
'''
def is_single_journey_time_within_team_constrains(distances, jobs, team):
    total_travel_time = max_single_travel_time_in_sec(distances, jobs, team)
    logger.debug('single travel time in sec {}, max team single journey: {}'.format(total_travel_time, team.max_single_journey_time_sec))
    return total_travel_time < team.max_single_journey_time_sec

'''
validate if total journey (here includes waiting and loading time) is within team's vehicle time constrains
'''
def is_total_journey_time_within_constrains(distances, solution):
    for team in solution.teams:
        jobs_seq = solution.get_job_seq_at(team.id).jobs_seq
        valid = is_total_journey_time_within_team_constrains(distances, jobs_seq.jobs, team)
        if not valid:
            return False

    return True

'''
is total journey within team constrains
'''
def is_total_journey_time_within_team_constrains(distances, jobs, team):
    total_time_in_secs = calculate_total_time_in_seconds(distances, jobs, team)
    logger.debug('total time in sec: {}, time available: {}'.format(total_time_in_secs, team.time_available_sec))
    return  total_time_in_secs < team.time_available_sec

'''
is jobs sequence valid
'''
def is_cadidate_valid(distances, jobs, team):
    logger.debug('validating  jobs: {}'.format(len(jobs.jobs)))
    v1 = is_distance_valid_for_job_vehicle(distances, jobs, team) # Missing  distance contraint
    v2 = is_journey_capacity_within_vehicle_constrain(jobs, team.vehicle) # total capacity contraint
    v3 = is_single_journey_time_within_team_constrains(distances, jobs, team)       # single journey time constraint (max)
    v4 = is_total_journey_time_within_team_constrains(distances, jobs, team) #total travel time constraint
    rs = v1 and v2 and v3 and v4 
    logger.debug('four validations: {}, {}, {}, {} = {}'.format(v1, v2, v3, v4, rs))
    return rs
        

'''
validate solution
'''
def validate_solution(distances, solution):
    v1 = is_distance_valid_for_vehicle(distances, solution)
    v2 = is_journey_capacity_within_constrains(solution)
    v3 = is_journey_time_within_constrains(distances, solution)
    v4 = is_total_journey_time_within_constrains(distances, solution)
    rs = v1 and v2 and v3 and v4 
    logger.debug('solution four validations: {}, {}, {}, {} = {}'.format(v1, v2, v3, v4, rs))
    return rs