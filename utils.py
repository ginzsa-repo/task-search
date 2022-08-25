
import json

'''
from solution
make a copy of the pre jobs list and post job addition list
'''
def clone_pre_post_jobs(solution, position,  job, team_idx):
    return clone_pre_post_to_jobs(position, solution.get_job_seq_at(team_idx).jobs_seq.jobs, job)


'''
make a copy of the pre jobs list and post job addition list
'''
def clone_pre_post_to_jobs(index, jobs, job):
    post = list(jobs)
    post.insert(index, job)
    return post


'''
load data and create distance matrix
json file with the following fields inside the path ('spDMResult'/'items'):
    href
    originSpId
    destinationSpId
    distance
    track
    transportMode
    lastUpdatedTime
'''
def create_distance_matrix_from_json_file(json_file_path):
    matrix = {}
    data = load_test_data(json_file_path)
    for item in data['spDMResult']['items']:
        
        frm = item.get('originSpId')
        if frm is not None:
            from_vector = matrix.get(frm, {})
            to_vector = from_vector.get(item['destinationSpId'])
            if to_vector is None:
                from_vector[item['destinationSpId']] = item
                matrix[frm] = from_vector

    return matrix

'''
load data from local file
'''
def load_test_data(file_path):

    with open(file_path) as json_file:
        data = json.load(json_file) 
        
    return data