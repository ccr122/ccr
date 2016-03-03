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
import numpy as np
from num2words import num2words

'''
exhibits = pandas dataframe filtered down by museums
dim = [ all the words in all descriptions (no duplicates) ]
comparisons = [ (exhibit1, exhibit2, theta),...]

We need to save and reopen exhibits,comparisons, and dim so its faster.
Also if we have time we should be able to update these data
    without reconstructing everything

'''

class Search():
    '''
    Contains things needed to search
    '''
    
    def __init__(self,exhibits_file):
        '''
        Makes lots of commonly cited calculations for later use
        '''
        exhibits = pd.read_csv(exhibits_file,dtype={'ex_id':str})
        self.words = list(exhibits['word'].unique())
        self.ex_list = exhibits['ex_id'].unique()
        self.num_ex  = len(self.ex_list)
        self.num_ex_with_word = {}
        for w in self.words:
            self.num_ex_with_word[w] = len(exhibits[exhibits['word']==w]['ex_id'].unique())
            
        self.ex_vects = self.vectorize_exhibits(exhibits)
        self.comparison_table = build_comparison_table()
    
    def tf_idf(self,term,document):
        '''
        term frequency-inverse document frequency (tf-idf)
        this normalizes a given word so rarer words are worth more
        '''
        term_frequency = document[term]             
        max_frequency_in_doc = max(document.values())    
        tf = .5 +.5*(term_frequency/max_frequency_in_doc)             
        num_rel_docs = 1 + self.num_ex_with_word.get(term,0)
        idf = np.log( self.num_ex/num_rel_docs ) 
        return tf*idf
        
    def vectorize_exhibits(self,exhibits):
        '''
        Makes tf_idf adjusted vector for each exhibit
        data stored in { museum: { ex_id : vector}}
        '''
        return {}
        
    #Not done
        
    def build_comparison_table(self,exhibits):
        '''
        Makes a pandas data frame comparing exhibits
        '''
        comparison = pd.dataframe(columns = self.ex_list, index = self.ex_list)
        
        for ex in self.ex_list():
            comparison[ex][ex] = 0.0
        for (ex1,ex2) in itertools.combinations(self.ex_list,2):
            v1 = self.ex_vects[ex1[:2]][ex1]
            v2 = self.ex_vects[ex2[:2]][ex1]
            d = spatial.distance.cosine(v1,v2)
            comparison[ex1][ex2] = d
            comparison[ex2][ex1] = d
        
        return comparison
    
    def compare_exhibits(self,ex_id,museums):
        '''
        return exhibits from given museums
        sorted by cosine similarity
        '''
        return []
        
    #Not done
    
    def vectorize_dict(self,key_words):
        '''
        takes a dictionary of key words, turns it into a tfidf adjusted vector
        '''
        v = []
        for w in self.words:
            x = key_words.get(w,0)
            assert type(x) == int
            v.append(self.tf_idf(x,key_words))
        return v
        
    def search(self,key_words,museums, num_results):
        '''
        Inputs:
            key_words from search queery - {word:word count}
            museums -   [museums to search from]
            num_results
        outputs:
            closest num_result museums from your museums of choice
        '''
        search_vect = self.vectorize_dict(key_words)
        results = []
        for m in museums:
            for ex in self.ex_vects[m]:
                dist = spatial.distance.cosine(search_vect,self.ex_vects[m][ex])
                results.append( (ex, dist))
        results.sort(key=lambda x: x[1])
        
        return results[ : min(len(results), num_results)]
        

##### Data related: getting and saving files, generating pandas tables

FILE_PATHS = {  
 #               'dim'           : 'pickled_dim',
#                'exhibits'      : 'pickled_exhibits',
                'comparison'    : 'comparison_table',
                'ex_desc_csv'   : '../csvs/ex_id_to_ex_desc_parsed.csv',
                'ex_dict'       : 'pickled_ex_dict',
                'search_object' : 'pickled_search_object'
                }
"""
def make_dim_exhibits():
    '''
    takes a list of museum ids: museums = ['001','002',...]
    makes dim - set of all words that appeared in dataframe
    makes filtered - dataframe filtered by museum
    '''
    exhibits = pd.read_csv( FILE_PATHS['ex_desc_csv'] ,dtype={'ex_id':str})
    dim = exhibits['word'].unique()
    return (dim, exhibits)

def make_ex_dict(exhibits):
    ex_dict = exhibits.groupby('ex_id').groups
    for x in ex_dict:
        rows = ex_dict[x]
        words = [exhibits.loc[ row,'word'] for row in rows]
        words_dict = {}
        for w in words:
            if words_dict.get(w) == None:
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
    (dim,exhibits) = make_dim_exhibits()
    ex_dict = make_ex_dict(exhibits)
    comparison = pd.DataFrame(  columns = ex_dict.keys(),
                            index = ex_dict.keys())
    for ex in ex_dict:
        comparison[ex][ex]=0.0
    for (ex1,ex2) in itertools.combinations(ex_dict,2):
        d = cosine_distance(ex_dict[ex1] ,ex_dict[ex2],dim,exhibits)
        comparison[ex1][ex2] = d
        comparison[ex2][ex1] = d
    
    comparison = comparision.rename(columns={comparison.columns[0]:'ex_id'})
    return comparison

def get_comparison_table():
    '''
    Checks if it is saved, builds if its not
    '''
    c = FILE_PATHS['comparison']
    if os.path.isfile(c):
        return pd.read_csv(c)
    else:
        comparison = build_comparison_table()
        comparison.to_csv(FILE_PATHS['comparison'])
    assert os.path.isfile(c)
    return pd.read_csv(c)
    
def get_ex_dict():
    '''
    checks if it is saved, builds if it is not
    '''
    fp = FILE_PATHS['ex_dict']
    
    if os.path.isfile(fp):
        with open(fp,'r') as pik:
            ex_dict = pickle.load(pik)
    else:
        (d,e) = make_dim_exhibits()
        ex_dict = make_ex_dict(e)
        with open(fp,'w') as pik:
            pickle.dump(ex_dict,pik)
    return ex_dict

def reset_files():
    '''
    For overwriting purposes
    '''
    for path in ['comprison','ex_dict']:
        os.remove( FILE_PATHS[path] )
    
        
######### Cosine similarity

def tfidf(t,d,D):
    '''
    term frequency-inverse document frequency
    this normalizes the corpus so rarer words are worth more
        t = term
        d = document
        D = { documents in corpus}
    '''
    return tf(t,d)*idf(t,D)
    
def tf(t,d):
    '''
    term_frequency = frequency(term,document)
    mnt = max{frequency(term',document) : term' in document }
    '''
    ft = d[t] 
    mnt = max(d.values())
    return .5 + .5*(ft/mnt)

def idf(t,D):
    '''
    N is number of documents
    Ndf is number of documents with term t
    '''
    N = len(D['ex_id'].unique())
    Ndf = len(D[D['word']==t]['ex_id'].unique())
    return np.log( N/Ndf )

def make_vector(words,dim,exhibits):
    '''
    Changes a dict of {word:word count}
    into list (vector)
    each entry is normalized by tfidf
    '''
    vect = []
    for t in dim:
        x = words.get(t)
        if x is not None:
            assert type(x)==int
            vect+=[tfidf(t,words,exhibits)]
        else:
            vect+=[0]
    return vect

def cosine_distance(words1,words2,dim,exhibits):
    '''
    Takes 2 dictionary of {word:word count} and list [all words]
    returns cosine similarity between words1,words2
    '''
    a = make_vector(words1,dim,exhibits)
    b = make_vector(words2,dim,exhibits)
    return spatial.distance.cosine(a,b)

###### Search tools

def find_similar_exhibits(e_id, num_results):
    '''
    Given an exhibit, returns the num_results most similar exhibitions
    trivially the most similar exhibition is itself so we skip that one.
    '''
    comparison = get_comparison_table()
    difference = comparison[e_id].sort_values()
    return difference.index[1,min(1+num_results,len(difference))]
    
def key_word_search(key_words,dim,exhibits):
    '''
    takes a dict {key word: number of times keyword occured}
    returns list of exhibits sorted by similarity (no orthogonal results)
    WARNING - I think we suffer from floating point error as some queeries
            return lots of 1s
    '''
    ex_dict = get_ex_dict()
    search_vect = make_vector(key_words,dim,exhibits)
    differences = [( x, spatial.distance.cosine(search_vect,make_vector(ex_dict[x],dim,exhibits)))
                    for x in ex_dict]
    differences.sort(key=lambda x: x[1])
    return differences
    #return [d[0] for d in differences if d[1]!=1] #filter out orthogonal seraches
"""


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

def get_search_object(force = False):
    '''
    checks if it is saved, builds if it is not
    '''
    fp = FILE_PATHS['search_object']
    
    if os.path.isfile(fp) or not force:
        with open(fp,'r') as pik:
            S = pickle.load(pik)
    else:
        with open(fp,'w') as pik:
            S = Search( FILE_PATHS['ex_desc_csv'] )
            pickle.dump( S ,pik)
    return S


def searchify(search_text):
    '''
    takes search term string
    returns dictionary {normalized_word : count}
    '''
    return{}

def search(args):
    '''
    Assuming we can get args_from_ui as a dict { 'field', ui input }
    we search things and return results
    '''
    key_words = searchify( args['seach_field'] )
    museums = args['museums']
    num_results = args['num_results']
    s = get_search_object()
    s.search(key_words,museums,num_results)
    
default_key_word_search = {'yellow':4,'brick':5,'road':2,'I':1,'love':4,'ART':2,'SqUaRE':1}