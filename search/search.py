# Search function
# Takes user keyword search and selected museums (if any) in a dictionary
# Returns top 5 museum exhibits
# also builds comparison table from scratch


from scipy import spatial
import itertools
import pandas as pd
import csv
import pickle


'''
exhibits = {ex_id: { word in decscription : number of occurance } }
dim = [ all the words in all descriptions (no duplicates) ]
comparisons = [ (exhibit1, exhibit2, theta),...]

We need to save and reopen exhibits,comparisons, and dim so its faster.
Also if we have time we should be able to update these data
    without reconstructing everything

'''


def make_dim_exhibits():
    
    
    dim = []
    exhibits = {}
    with open('../csvs/ex_id_to_ex_desc_parsed.csv') as f:
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
    return (dim,exibits)
                

def make_vector(words):
    vect = []
    for d in dim:
        x = words.get(d)
        if x == None:
            vect+=[0]
        else:
            assert type(x)==int
            vect+=[x]
    return vect

def cosine_similarity(words1,words2):
    '''
    Takes 2 dictionary of {word:word count} and list [all words]
    returns cosine similarity between words1,words2
    '''
    a = make_vector(words1)
    b = make_vector(words2)
    return spatial.distance.cosine(a,b)


def build_comparison_table(exhibits):
    '''
    Makes table of cosine_similarity between descriptions
    index and columns are all exhibit ids
    '''
    comparison = pd.DataFrame(columns = exhibits.keys(),index = exhibits.keys())
    
    for ex in exhibits.keys():
        comparison[ex][ex]=0.0
    for (ex1,ex2) in itertools.combinations(exhibits.keys(),2):
        difference = cosine_similarity(exhibits[ex1] ,exhibits[ex2])
        comparison[ex1][ex2] = difference
        comparison[ex2][ex1] = difference
        
    return comparison



def update_comparison_table(exhibits,comparison):
    '''
    In case we decide to get more museums we should update comparison
    rather than build it from scratch
    '''
    pass

def find_similar_exhibits(museum_id, num_results):
    '''
    Given an exhibit, returns the num_results most similar exhibitions
    trivially the most similar exhibition is itself so we skip that one.
    '''
    difference = comparison[museum_id].sort_values()
    return difference.index[1,1+num_results]
    
def key_word_search(key_words):
    k_vect = make_vector(key_words)
    best=(None,None)
    for c in exhibits:
        c_vect = make_vector(exhibits[c])
        difference = cosine_similarity(k_vect, c_vect)
        if difference < best[1]:
            best = (c,difference)
    return best[0]
        
(dim,exhibits) = make_dim_exhibits()
comparison     = build_comparison_table(exhibits)

def get_files(s):
    path = {   'dim'       : 'pickled_dim'
        'exhibits'  : 'pickled_exhibits'
        'comparison': 'pickled_comparison'}
    with open