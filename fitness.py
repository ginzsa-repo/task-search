
from travel_calculator import sum_no_items_in_jobs, calculate_total_time_in_seconds


def calculate_fitness(config, distances, solution):
    fitness = 0.0
    for team in solution.teams:
        fitness += job_fitness(config, distances, solution.get_job_seq_at(team.id).jobs_seq, team)
    return fitness


'''
calculate job fitness
'''
def job_fitness(config, distances, jobs_seq, team):
    items = min(sum_no_items_in_jobs(jobs_seq.jobs), team.vehicle.capacity)
   
    total_travel_time = calculate_total_time_in_seconds(distances, jobs_seq, team)

    item_weight = config['item_weight']
    time_weight = config['time_weight']

    return (items * item_weight) - (total_travel_time * time_weight)
