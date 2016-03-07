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
import csv
#from parse import str_to_dict
'''
This function contains the search object and helper functions for django to call

'''

NUM_SIMILARS    = 5
NUM_RESULTS     = 10


def make_file_paths(path_to_searchpy = ''):
    '''
    dict to relevant urls
    needs path_to_searchpy if imported into another file - like Django's views
    '''
    assert type(path_to_searchpy) == str
    FILE_PATHS = {  
                'ex_desc_csv'   : 'csvs/ex_id_to_ex_desc_parsed.csv',
                'search_object' : 'pickled_search_object',
                'title'         : 'csvs/ex_id_to_ex_title.csv',
                'url'           : 'csvs/ex_id_to_ex_url.csv'
                }
    return {  k : path_to_searchpy + v for k,v in FILE_PATHS.items() }



class Search():
    '''
    This object is here to make and then hold
    a lot of commonly cited calculations for later use
    with regards to cosine similarity document searches anyway
    It gets pickled
    ''' 
    def __init__(self,exhibits_file):
        '''
        Run ALL the calculations
        '''
        exhibits = pd.read_csv(exhibits_file,dtype={'ex_id':str})
        self.words = list(exhibits['word'].unique())
        self.ex_list = list(exhibits['ex_id'].unique())
        self.num_ex  = len(self.ex_list)
        self.museums = {x[:3] for x in self.ex_list}
        self.num_ex_with_word = {}
        for w in self.words:
            self.num_ex_with_word[w] = len(exhibits[exhibits['word']==w]['ex_id'].unique())
        self.ex_vects = self.vectorize_exhibits(exhibits)
        self.comparison_table = self.build_comparison_table()
    
    def tf_idf(self,term,document):
        '''
        term frequency-inverse document frequency (tf-idf)
        this normalizes a given word so rarer words are worth more
        '''
        term_frequency = float(document.get(term,0.0) )          
        max_frequency_in_doc = float(max(document.values()) )   
        tf = 50.0*(term_frequency/max_frequency_in_doc)  
        num_rel_docs = 1.0 + self.num_ex_with_word.get(term,0)
        idf = np.log( float(self.num_ex)/float(num_rel_docs) ) 
        return tf*idf

    def vectorize_dict(self,key_words):
        '''
        takes a dictionary of key words, turns it into a tfidf adjusted vector
        '''
        v = []
        for w in self.words:
            v.append(self.tf_idf(w,key_words))
        return v

    def vectorize_exhibits(self,exhibits):
        '''
        Makes tf_idf adjusted vector for each exhibit
        data stored in { ex_id : vector }
        '''
        ex_dics = {}
        for e in self.ex_list:
            ex_dic = { k:len(v) for k,v in 
                exhibits[exhibits['ex_id']==e].groupby('word').groups.items() }
            ex_dics[e] = self.vectorize_dict(ex_dic) 
        return ex_dics
        
    def build_comparison_table(self):
        '''
        Makes a pandas data frame comparing exhibits
        '''
        comparison = pd.DataFrame(columns = self.ex_list, index = self.ex_list)
        for ex in self.ex_list:
            comparison[ex][ex] = 0.0
        for (ex1,ex2) in itertools.combinations(self.ex_list,2):
            v1 = self.ex_vects[ex1]
            v2 = self.ex_vects[ex2]
            d = spatial.distance.cosine(v1,v2)
            comparison[ex1][ex2] = d
            comparison[ex2][ex1] = d
        return comparison
    
    def similar_exhibits(self,ex_id,museums,num_results):
        '''
        return exhibits from given museums
        sorted by cosine similarity
        '''
        if len(museums) == 0:
            museums = self.museums
        res = [x for x in self.comparison_table[ex_id].iteritems()
                if x[0][:3] in museums]
        res.sort(key = lambda x:x[1])
        return [r[0] for r in res][1:min(len(res),num_results+1)]
        
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
        res     = []
        if len(museums) == 0:
            museums = self.museums
        for ex in [x for x in self.ex_list if x[:3] in museums]:
            dist = spatial.distance.cosine(search_vect,self.ex_vects[ex])
            print(str(ex)+'\t'+str(dist))
            if dist < 1.0:
                res.append( (ex, dist) ) 
        res.sort(key=lambda x: x[1]) 
        return [r[0] for r in res]

    def get_similar_results(self,ex_id,museums,path_to_searchpy = ''):
        '''
        Given exhibit ID and seleced museums, similar_exhibits at those museums
        '''
        num_results = NUM_SIMILARS
        res = self.similar_exhibits(ex_id,museums,num_results)
        return [ (  get_ex_attribute( r, 'url'  , path_to_searchpy),
                    get_ex_attribute( r, 'title', path_to_searchpy)  )
                for r in res ]

    def get_results(self,args,path_to_searchpy = ''):
        '''
        Take args and use serach engine
        '''
        num_results = NUM_RESULTS
        key_words  = str_to_dict(args.get('text')) 
        museums     = args.get('museums')
        res = self.search(key_words,museums,num_results)

        if len(res) == 0:
            return [(' ','No results', None )]

        results = []
        for r in res:
            u = get_ex_attribute( r, 'url'  , path_to_searchpy)
            t = get_ex_attribute( r, 'title', path_to_searchpy)
            s = self.get_similar_results(r, museums,path_to_searchpy)
            results += [(u,t,s)]
        return results

#### Helper functions

def get_ex_attribute(ex_id,attribute,path_to_searchpy=''):
    '''
    Given ex_id and attribute, returns that exhibit's attribute
    '''
    assert attribute in ['url','title']
    file_paths = make_file_paths(path_to_searchpy)

    fp = file_paths[attribute]
    with open( fp ) as f:
        reader = csv.reader(f, delimiter='|')
        next(reader)
        for row in reader:
            if ex_id == row[0]:
                return row[1]

############# Theses guys interact with Django

def get_search_object(path_to_searchpy = '',force = False):
    '''
    checks if it is saved, builds if it is not
    '''
    file_paths = make_file_paths(path_to_searchpy)
    fp = file_paths['search_object']
    if os.path.isfile(fp) and not force:
        print('found pickled search object')
        try:
            with open(fp,'r') as pik:
                S = pickle.load(pik)
            return S
        except ImportError:
            print ( '\timport error')
    print('making pickle and search object')
    with open(fp,'w') as pik:
        S = Search( path_to_searchpy + file_paths['ex_desc_csv'] )
        pickle.dump(S,pik)
    return S


def str_to_dict(s):
    words = {}
    for i in s.split():
        if i in words:
            words[i] += 1
        else:
            words[i] = 1
    return words

