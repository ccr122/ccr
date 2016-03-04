# Search function
# Takes user keyword search and selected museums (if any) in a dictionary
# Returns top 5 museum exhibits
# also builds comparison table from scratch
from scipy import spatial
import itertools
import pandas as pd
import csv
import pickle
import os.path
import re

'''
exhibits = {ex_id: { word in decscription : number of occurance } }
dim = [ all the words in all descriptions (no duplicates) ]
comparisons = [ (exhibit1, exhibit2, theta),...]

We need to save and reopen exhibits,comparisons, and dim so its faster.
Also if we have time we should be able to update these data
    without reconstructing everything

'''
FILE_PATHS = {  'dim'         : 'pickled_dim',
                'exhibits'    : 'pickled_exhibits',
                'comparison'  : 'pickled_comparison',
                'ex_desc_csv' : '../csvs/ex_id_to_ex_desc_parsed.csv'
                }

def make_dim_exhibits():
    '''
    This function reads the parsed exhibits and returns (dim,exhibits) 
    dim is a list of [all words]
    exhibits is a dict that maps exhibit_id to a dict that maps word
    to number of occurances in that exhibit's description/title
    '''  
    dim = []
    exhibits = {}
    with open(FILE_PATHS['ex_desc_csv']) as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            ex_id = row[0]
            w = row[1]
            if ex_id not in exhibits:
                exhibits[ex_id] = {}
            if w not in exhibits[ex_id]:
                exhibits[ex_id][w] = 0
            exhibits[ex_id][w] += 1
            
            if w not in dim:
                dim.append(w)
    with open(FILE_PATHS['dim'],'w') as f:
        pickle.dump(dim,f)
        f.close()
    with open(FILE_PATHS['exhibits'],'w') as g:
        pickle.dump(exhibits,g)
        g.close()

def make_vector(words,dim):
    vect = []
    for d in dim:
        x = words.get(d)
        if x == None:
            vect+=[0]
        else:
            assert type(x)==int
            vect+=[x]
    return vect

def cosine_distance(words1,words2,dim):
    '''
    Takes 2 dictionary of {word:word count} and list [all words]
    returns cosine similarity between words1,words2
    '''
    a = make_vector(words1,dim)
    b = make_vector(words2,dim)
    return spatial.distance.cosine(a,b)

def build_comparison_table():
    '''
    Makes table of cosine_distance between descriptions
    index and columns are all exhibit ids
    '''
    exhibits = get_files('exhibits')
    comparison = pd.DataFrame(  columns = exhibits.keys(),
                                index = exhibits.keys())
    
    for ex in exhibits.keys():
        comparison[ex][ex]=0.0
    for (ex1,ex2) in itertools.combinations(exhibits.keys(),2):
        d = cosine_distance(exhibits[ex1] ,exhibits[ex2],dim)
        comparison[ex1][ex2] = d
        comparison[ex2][ex1] = d
        
    with open(FILE_PATHS['comparison'],'w') as f:
        pickle.dump(comparison,f)
        f.close()

def update_comparison_table(exhibits,comparison):
    '''
    In case we decide to get more museums we should update comparison
    rather than build it from scratch
    '''
    pass

def get_pickled_files(s):
    path = FILE_PATHS[s]
    if os.path.isfile( path ):
        with open( path ,'r') as f:
            return pickle.load(f)
    else:
        return None

def get_files(s):
    unpickled = get_pickled_files(s)
    if unpickled is not None:
        return unpickled
    else:
        FILE_MAKERS = {'dim' : make_dim_exhibits,
                    'exhibits' : make_dim_exhibits,
                    'comparison' : build_comparison_table}
        FILE_MAKERS[s]()
        unpickled = get_pickled_files(s)
        assert unpickled is not None
        return unpickled

############## EVERYTHING BEFORE THIS IS BUT HELPER FUNCTIONS
############## THESE BE THE TRU HEROS BEFORE YE

def find_similar_exhibits(museum_id, num_results):
    '''
    Given an exhibit, returns the num_results most similar exhibitions
    trivially the most similar exhibition is itself so we skip that one.
    '''
    difference = comparison[museum_id].sort_values()
    return difference.index[1,1+num_results]
    
def key_word_search(key_words,num_results):
    '''
    takes a dict {key word: number of times keyword occured}
    returns list of num_results most similar exhibits
    WARNING - I think we suffer from floating point error as some queeries
            return lots of 1s
    '''
    dim, exhibits = ( get_files(s) for s in ('dim','exhibits') )
    differences = [( x, cosine_distance(key_words,exhibits[x],dim) )
                    for x in exhibits]
    differences.sort(key=lambda x: x[1])
    return differences[:min(num_results,len(differences))]

def searchify(search_string):
    '''
    inputs: string
    ou
    removes plurals 
    '''
    search_string.split(' ')
    
    
    
    ### turn numbers into words