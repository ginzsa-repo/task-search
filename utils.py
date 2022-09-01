
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
load data and create distance matrix
use distance key mapper and path
expected key: items_path, origin, destination
'''
def create_distance_matrix_from_json_file_mapper(distance_mapper, json_file_path):
    matrix = {}
    data = load_test_data(json_file_path)

    items_path = distance_mapper['items_path'] # e.g.: 'spDMResult/items'

    items = path_navigate_to_object(data, items_path)
    origin = distance_mapper['origin']
    destination = distance_mapper['destination']

    for item in items:
        
        frm = item.get(origin)
        if frm is not None:
            from_vector = matrix.get(frm, {})
            to_vector = from_vector.get(item[destination])
            if to_vector is None:
                from_vector[item[destination]] = item
                matrix[frm] = from_vector

    return matrix

'''
load data from local file
'''
def load_test_data(file_path):

    with open(file_path) as json_file:
        data = json.load(json_file) 
        
    return data

'''
navigate dict path 
default separator = '/'
not found return none object
'''
def path_navigate_to_object(to_navigate, path_string, separator='/'):
    path = path_string.split(separator)
    a = to_navigate
    for i in path:
        rs =  a.get(i)
        if type(rs) is not  dict:
                return rs
                break
        else:
            a = rs