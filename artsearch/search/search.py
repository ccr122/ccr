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
from scrapers.parse import str_to_dict
from parse import str_to_dict
'''
search object and helper functions
'''

NUM_SIMILARS    = 5
NUM_RESULTS     = 10



class Search():
    '''
    This object generates and holds everything needed for search:
        document vectors, for each exhibit
        common TF_IDF calculations
        comparison table
    ''' 
    def __init__(self,exhibits_file):
        '''
        Inputs:
            exhibis file csv ex_id | word
        '''
        exhibits = pd.read_csv(exhibits_file,dtype={'ex_id':str},delimiter='|')
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
        gives each term in a document an identification score
            indicating how important it is to identifying document vectors
        tf measures importance of word to document
        idf measures rarity of word in corpus
        '''
        term_frequency = float(document.get(term,0.0) )          
        max_frequency_in_doc = float(max(document.values()) )   
        tf = 50.0*(term_frequency/max_frequency_in_doc)  
        num_rel_docs = 1.0 + self.num_ex_with_word.get(term,0)  #add by 1 to avoid div by 0
        idf = np.log( (1.0 + self.num_ex)/float(num_rel_docs) )  #add 1 to numerator so we can get log(1)=0 if term in all documents (eg 'the')
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
        
    def search(self,key_words,museums):
        '''
        Inputs:
            key_words from search queery - {word:word count}
            museums -   [museums to search from]
        outputs:
            closest exhibits from your museums of choice
        '''
        search_vect = self.vectorize_dict(key_words)
        res     = []
        if len(museums) == 0:
            museums = self.museums
        for ex in [x for x in self.ex_list if x[:3] in museums]:
            dist = spatial.distance.cosine(search_vect,self.ex_vects[ex])
            if dist < 1.0:
                res.append( (ex, dist) ) 
        res.sort(key=lambda x: x[1]) 
        return [r[0] for r in res]

    def get_similar_results(self,ex_id,museums,path_to_search_dir = ''):
        '''
        Given exhibit ID and seleced museums, similar_exhibits at those museums
        '''
        res = self.similar_exhibits(ex_id, museums, NUM_SIMILARS)
        return [ (  get_ex_attribute( r, 'url'  , path_to_search_dir),
                    get_ex_attribute( r, 'title', path_to_search_dir)  )
                for r in res ]

    def get_results(self,args,path_to_search_dir = ''):
        '''
        Take args and use serach engine
        '''
        num_results = NUM_RESULTS
        key_words  = str_to_dict(args.get('text')) 
        museums     = args.get('museums')
        res = self.search(key_words,museums)

        if len(res) == 0:
            return None

        results = []
        for r in res:
            u = get_ex_attribute( r, 'url'  , path_to_search_dir)
            t = get_ex_attribute( r, 'title', path_to_search_dir)
            s = self.get_similar_results(r , museums, path_to_search_dir)
            d = get_ex_attribute( r, 'date' , path_to_search_dir)
            results += [(u,t,s,d)]
        return results

#### Helper functions

def make_file_paths(path_to_search_dir = ''):
    '''
    dict to relevant urls
    needs path_to_search_dir if imported into another file - like Django's views
    '''
    assert type(path_to_search_dir) == str
    FILE_PATHS = {  
                'ex_desc_csv'   : 'csvs/exid_word.csv',
                'search_object' : 'pickled_search_object',
                'title'         : 'csvs/exid_title.csv',
                'url'           : 'csvs/exid_url.csv',
                'date'          : 'csvs/exid_date.csv'
                }    
    return {  k : path_to_search_dir + v for k,v in FILE_PATHS.items() }

def get_search_object(path_to_search_dir = '',force = False):
    '''
    by default gets seach object from a pickle,
    if that fails or if force =True
    then generate a new of search object
    '''
    file_paths = make_file_paths(path_to_search_dir)
    fp = file_paths['search_object']
    if os.path.isfile(fp) and not force:
        print('found pickled search object')
        try:
            with open(fp,'r') as pik:
                S = pickle.load(pik)
            print('got it!')
            return S
        except:
            print ( '\t error loading pickle')
    print('making new search object and pickle')
    with open(fp,'w') as pik:
        S = Search(file_paths['ex_desc_csv'] )
        pickle.dump(S,pik)
    print('made it!')
    return S

def get_ex_attribute(ex_id,attribute,path_to_search_dir=''):
    '''
    Given ex_id and attribute, returns that exhibit's attribute
    '''
    assert attribute in ['url','title','date']
    file_paths = make_file_paths(path_to_search_dir)
    fp = file_paths[attribute]
    with open( fp ) as f:
        reader = csv.reader(f, delimiter='|')
        next(reader)
        for row in reader:
            if ex_id == row[0]:
                return row[1]