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
exhibits = pandas dataframe filtered down by museums
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

def make_ex_dict(exhibits):
    ex_dict = exhibits.groupby('ex_id').groups
    for x in ex_dict:
        rows = ex_dict[x]
        words = [exhibits.loc[ row,'word'] for row in rows]
        words_dict = {}
        for w in words:
            if words_dict.get(w)==None:
                words_dict[w] = 1
            else:
                words_dict[w] += 1
        ex_dict[x] = words_dict
    return ex_dict

def build_comparison_table():
    '''
    Makes table of cosine_distance between descriptions
    index and columns are all exhibit ids
    '''
    (dim,exhibits) = make_dim_exhibits(None)
    ex_dict = make_ex_dict(exhibits)
    comparison = pd.DataFrame(  columns = ex_dict.keys(),
                            index = ex_dict.keys())
    for x in ex_dict:
        comparison[ex][ex]=0.0
    for (ex1,ex2) in itertools.combinations(ex_dict,2):
        d = cosine_distance(ex_dict[ex1] ,ex_dict[ex2],dim)
        comparison[ex1][ex2] = d
        comparison[ex2][ex1] = d
    
    comparison = comparision.rename(columns={c.columns[0]:'ex_id'})
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

###### Search tools

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
    returns list of exhibits sorted by similarity (no orthogonal results)
    WARNING - I think we suffer from floating point error as some queeries
            return lots of 1s
    '''
    ex_dict = make_ex_dict(exhibits)
    dim |= set(key_words.keys())
    differences = [( x, cosine_distance(key_words,ex_dict[x],dim) )
                    for x in ex_dict]
    differences.sort(key=lambda x: x[1])
    return [d[0] for d in differences if d[1]!=1] #filter out orthogonal seraches

def searchify(search_string):
    '''
    inputs: string
    output: dictionary {word: count}
    removes plurals 
    '''
    wordre = "[A-Za-z0-9'-]"
    l = re.findall()
    
    ### turn numbers into words
    ### remove capitals
    ### also apply this function to parsing scraped data
    

    
##### Search main
'''
Assuming args_from_ui is something like
args = {
            'date_lower'    : dd/mm/yyyy
            'date_upper'    : dd/mm/yyyy
            'search_terms'  : 'blah blah blah'
            'Museums'       : ['001','002',...]
            'order_by'      : 'date_asc' or 'date_dec' or 'search'
        }
        
also possible to implement 'more like this' functionality
where user clicks on an exhibit and we return similar exhibits (possibly filtered too)

search should return:
    ( (Headers), [ (results) ] )
    ranked by search similarity or by date or something
'''

def search(args):
    '''
    Assuming we can get args_from_ui as a dict { 'field', ui input }
    we search things and return results
    '''
    (dim,exhibits)=args.get('museums')
    key_words = serachify[args['search_terms']]
    search_results = key_word_search(key_words,dim,exhibits)
    
default_key_word_search = {'yellow':4,'brick':5,'road':2,'I':1,'love':4,'ART':2,'SqUaRE':1}