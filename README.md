# task-search-optimizer

Self contained TABU search algorithm implementation (bico data)
Initial python version of task search optimizer project (not finished) 



# how to test it with data

```
python ./test/test_optimizer.py 
```

NOTE: unfinished some test might fail


# distance metric standarized mapping

First step load locations
map location:
data path: 'spList/items'
e.g.:
{'id':''spId', 'x':'lng', 'y':'lat', 'meta':{}}
location
- id
- x (longitude)
- y (latitude)
- meta

Second step create distance matrix
map distance matrix
data path: 'spDMResult/items'
e.g.: 
distance will have the default map of 'distance'
meta: will include the remaining data.
{'origin': 'originSpId', 'destination':'destinationSpId', 'meta':{}}

simplfy standards and map data
- origin
- destination
- distannce
- meta
