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

##### Data related: getting and saving files, generating pandas tables

FILE_PATHS = {  'dim'         : 'pickled_dim',
#                'exhibits'    : 'pickled_exhibits',
                'comparison'  : 'comparison_table',
                'ex_desc_csv' : '../csvs/ex_id_to_ex_desc_parsed.csv'
                }

def make_dim_exhibits(museums):
    '''
    takes a list of museum ids: museums = ['001','002',...]
    makes dim - set of all words that appeared in dataframe
    makes filtered - dataframe filtered by museum
    '''
    exhibits = pd.read_csv( FILE_PATHS['ex_desc_csv'] )
    if museums is not None:
        filter_ = [str(x) for x in exhibits['ex_id']]
        museums = [m.lstrip('0') for m in museums]
        filter_ = [ x[:-2] in museums for x in filter_]
        exhibits = exhibits[filter_]
    dim = set(exhibits.groupby('word').groups.keys())
    return (dim, exhibits)

def build_comparison_table():
    '''
    Makes table of cosine_distance between descriptions
    index and columns are all exhibit ids
    '''
    (dim,exhibits) = make_dim_exhibits(None)
    comparison = pd.DataFrame(  columns = exhibits.keys(),
                                index = exhibits.keys())
                                
    ex_dict = exhibits.groupby('ex_id')
    for x in ex_dict:
        rows = ex_dict[x]
        words = [exhibits.loc[ row,'word'] for row in rows]
        ex_dict[x] = words
    
    for ex in ex_dict:
        comparison[ex][ex]=0.0
    for (ex1,ex2) in itertools.combinations(ex_dict,2):
    
        d = cosine_distance(ex_dict[ex1] ,ex_dict[ex2],dim)
        comparison[ex1][ex2] = d
        comparison[ex2][ex1] = d
        
    comparison.to_csv(FILE_PATHS['comparison'])
    
def update_comparison_table(exhibits,comparison):
    '''
    In case we decide to get more museums we should update comparison
    rather than build it from scratch
    '''
    pass

def get_comparison_table():
    c = FILE_PATHS['comparison']
    if os.path.isfile(c):
        return pd.read_csv(c)
    else:
        build_comparison_table() #makes and saves table
    assert os.path.isfile(c)
    return pd.read_csv(c)

######### Cosine similarity

def make_vector(words,dim):
    '''
    Changes a dict of {word:word count}
    into list (vector)
    '''
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



############## EVERYTHING BEFORE THIS IS BUT HELPER FUNCTIONS
############## THESE BE THE TRU HEROS BEFORE YE


    

def find_similar_exhibits(museum_id, num_results):
    '''
    Given an exhibit, returns the num_results most similar exhibitions
    trivially the most similar exhibition is itself so we skip that one.
    '''
    difference = comparison[museum_id].sort_values()
    return difference.index[1,1+num_results]
    
def key_word_search(key_words,dim,exhibits):
    '''
    takes a dict {key word: number of times keyword occured}
    returns list of num_results most similar exhibits
    WARNING - I think we suffer from floating point error as some queeries
            return lots of 1s
    '''
    dim |= set(key_words.keys())
    
    differences = [( x, cosine_distance(key_words,exhibits[x],dim) )
                    for x in exhibits]
    differences.sort(key=lambda x: x[1])
    return [d for d in differences if d[1]!=1] #filter out orthogonal seraches
    
    
def search(args):
    '''
    Assuming we can get args_from_ui as a dict { 'field', ui input }
    we search things and return results
    '''
    (dim,exhibits)=args['museums']
    key_words = serachify[args['search_terms']]
    search_results = key_word_search(key_words,dim,exhibits)
    


wordre = "[A-Za-z0-9'-]"
def searchify(search_string):
    '''
    inputs: string
    output: dictionary {word: count}
    removes plurals 
    '''
    
    l = re.findall()
    
    
    ### turn numbers into words
    ### remove capitals
    
default_search = {'yellow':4,'brick':5,'road':2,'I':1,'love':4,'ART':2}