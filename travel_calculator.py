from asyncio.log import logger
from model import JobsSequence
from model import TeamJobs


'''
calculate total time in seconds
'''
def calculate_total_time_in_seconds(distances, jobs_seq, team):
    rs1 = total_travel_time_in_sec(distances, jobs_seq, team)
    rs2 = calc_load_time_seconds(jobs_seq, team.vehicle)
    rs3 = calc_stopping_time_seconds(jobs_seq, team.vehicle)
    return (rs1 + rs2 + rs3)


'''
extract jobs to process depending the type
'''
def extract_jobs_to_process(to_measure):
    if type(to_measure) == TeamJobs:
        to_measure =  to_measure.jobs_seq

    if type(to_measure) == JobsSequence: # start and end included
        jobs_to_process = [to_measure.start] + to_measure.jobs + [to_measure.end]
    else:
        # assumed is a list with start and end points
        jobs_to_process = to_measure

    return jobs_to_process

'''
calculate travel time for a job sequence
this function includes start and end service points
'''
def total_travel_time_in_sec(distances, to_measure, team):
    travel_time = 0

    jobs_to_process = extract_jobs_to_process(to_measure)
    
    previous_job = None
    for job in jobs_to_process:
        if previous_job is not None:
            travel_time += int(distances.get_travel_time(previous_job, job, team.vehicle.speed)) # note: as implementation, converted to int
        previous_job = job
    return travel_time

'''
return max single jouney time
'''
def max_single_travel_time_in_sec(distances, to_measure, team):
    max_time = 0

    jobs_to_process = extract_jobs_to_process(to_measure)
    
    previous_job = None
    for job in jobs_to_process:
        if previous_job is not None:
            max_time = max(int(distances.get_travel_time(previous_job, job, team.vehicle.speed)), max_time) # note: as implementation, converted to int
        previous_job = job
    return max_time

'''
return time in seconds for the stopping time in each job 
'''
def calc_stopping_time_seconds(jobs_seq, vehicle):
    # +1 includes end stop
    jobs = jobs_sequence_or_list(jobs_seq)
    return (len(jobs) + 1) * vehicle.avg_stopping_time_sec

'''
return time in seconds, corresponding to the sum of time taken to handle each job 
'''
def calc_load_time_seconds(jobs_seq, vehicle):
    return total_no_items(jobs_seq, vehicle) * vehicle.avg_load_time_sec

'''
return the minimum value betwee:
    sum number of items in a jobs sequence
    vehicle capacity
'''
def total_no_items(jobs_seq, vehicle):

    jobs = jobs_sequence_or_list(jobs_seq)

    total_items = 0
    for job in jobs:
        total_items += int(job[1])

    return min(total_items, vehicle.capacity)

'''
handle jobs list or job sequence
'''
def jobs_sequence_or_list(jobs_seq):
    # 
    if type(jobs_seq) == list: 
        jobs = jobs_seq
    else:
        jobs =  jobs_seq.jobs
    return jobs

'''
sum number of items except last one
'''
def sum_no_items_except_last_job(jobs_seq):
    return sum_no_items_in_jobs(jobs_seq.jobs[:-1])

def sum_no_items_in_jobs(jobs):
    count = 0
    for j in jobs:
        count += j[1]

    return count