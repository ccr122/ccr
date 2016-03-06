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

'''
exhibits = pandas dataframe filtered down by museums
dim = [ all the words in all descriptions (no duplicates) ]
comparisons = [ (exhibit1, exhibit2, theta),...]

We need to save and reopen exhibits,comparisons, and dim so its faster.
Also if we have time we should be able to update these data
    without reconstructing everything

'''
FILE_PATHS = {  
                'ex_desc_csv'   : 'csvs/ex_id_to_ex_desc_parsed.csv',
                'search_object' : 'pickled_search_object',
                'title'        : 'csvs/ex_id_to_ex_title.csv',
                'url'          : 'csvs/ex_id_to_ex_url.csv'
                }

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
            if dist < 1.0:
                res.append( (ex, dist) ) 
        res.sort(key=lambda x: x[1]) 
        return [r[0] for r in res]

#### Helper functions

def get_search_object(path_to_searchpy = '',force = False):
    '''
    checks if it is saved, builds if it is not
    '''
    fp = path_to_searchpy + FILE_PATHS['search_object']
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
        S = Search( path_to_searchpy + FILE_PATHS['ex_desc_csv'] )
        pickle.dump(S,pik)
    return S

def get_ex_attribute(ex_id,attribute,path_to_searchpy=''):
    '''
    Given ex_id and attribute, returns that exhibit's attribute
    '''
    assert attribute in ['url','title']

    fp = path_to_searchpy + FILE_PATHS[attribute]
    with open( fp ) as f:
        reader = csv.reader(f, delimiter='|')
        next(reader)
        for row in reader:
            if ex_id == row[0]:
                return row[1]

def str_to_dict(s):
    '''
    input: string
    output: dictionary {word: count}
    '''
    word_dict = {}
    l = re.findall(wordre, s)
    for i in range(len(l)):
        if type(l[i])== int:             # turn numbers into words
            l[i] = num2words(l[i])
        
        l[i] = l[i].lower()             # make all letters lowercase 
        
        if l[i][0] == "'":              # remove single quotes from beginning/
            l[i] = l[i][1:]             # end of words in l
        elif l[i][-1] == "'":
            l[i] = l[i][:-1]
            
        if l[i] not in INDEX_IGNORE:
            if l[i] not in word_dict:   # build dictionary
                word_dict[l[i]] = 1
            else:
                word_dict[l[i]] += 1
            
    words = word_dict.keys()            # remove plurals
    for i in range(len(words)):
        if words[i][-1] == 's':
            if words[i][:-1] == words[i-1]:
                word_dict[i-1] += word_dict[i]
                del word_dict[i]
        elif words[i][-1] == 'es':
            if words[i][:-2] == words[i-1]:
                word_dict[i-1] += word_dict[i]
                del word_dict[i]
    
    return word_dict

############# Theses guys interact with Django

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

def find_similar_exhibits(args,museums):
    '''
    args = {    ex_id: similar to this guy
                museums: ['001',...]            }
    '''
    ex_id   = args['ex_id']
    museums = args['museums']
    assert type(ex_id)==str
    assert type(museums)==list
    s = get_search_object()
    s.similar_exhibits(ex_id,museums)

default_key_word_search = {'yellow':4,'brick':5,'road':2,'I':1,'love':4,'ART':2,'SqUaRE':1}