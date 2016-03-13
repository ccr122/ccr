import re 
from nltk.stem.snowball import EnglishStemmer

import json

wordre = "[A-Za-z0-9'-]+"

def str_to_dict(s):
    '''
    input:  s string
    output: dictionary {word: count}
    '''
    s = s.encode('ascii','ignore')
    s = str(s)
    word_dict = {}
    l = re.findall(wordre, s)
    print(l)
    for w in l:
        w = w.lower()               # make all letters lowercase 
        
        if w[0] == "'":             # remove single quotes from beginning/
            w = w[1:]               # end of words in l
        elif w[-1] == "'":
            w = w[:-1]
        
        w = EnglishStemmer().stem(w)        # stems non-noun/verbs 
        w = w.encode('ascii','ignore')
        
        if w != '':
            if w not in word_dict:      # build dictionary
                word_dict[w] = 1
            else:
                word_dict[w] += 1

    return word_dict

def build_word_dict(index):
    '''
    input:  index (the dict passed from scraping)
    output: word_dict {word: ct}
    '''
    word_dict = {}
    for museum_id in index:
        word_dict[museum_id] = {}
        for ex_id in index[museum_id]:
            word_dict[museum_id][ex_id] = {}
            words =  index[museum_id][ex_id]['title'] 
            words += index[museum_id][ex_id]['desc']
            word_dict[museum_id][ex_id] = str_to_dict(words)
    return word_dict

def create_wordct_csv(word_ct_dict):
    '''
    input:  word_ct_dict {word: ct}
            filename for csv output
    save csv as filename --> ex_id|word
    '''
    with open('exid_word.csv','w') as f:
        line = 'ex_id|word\n'
        f.write(line)
        for museum_id in word_ct_dict:
            for ex_id in word_ct_dict[museum_id]:
                for word in word_ct_dict[museum_id][ex_id]:
                    ct = 0
                    while ct < word_ct_dict[museum_id][ex_id][word]:        # check this! 
                        line = '{}|{}\n'.format(str(ex_id), str(word))
                        f.write(line)
                        ct += 1

ATTR_DICT = {   'title' : '../csvs/exid_title.csv', 
                'date'  : '../csvs/exid_date.csv' ,
                'url'   : '../csvs/exid_url.csv'   }

def create_attr_csvs(index):
    for attr in ATTR_DICT:
        with open(ATTR_DICT[attr],'w') as f:
            line = 'ex_id|' + attr + '\n'
            f.write(line)
            for museum_id in index:
                for ex_id in index[museum_id]:
                    line = '{}|{}\n'.format(str(ex_id), \
                        index[museum_id][ex_id][attr].encode('ascii','ignore'))
                    f.write(line)   

def json_to_csvs(index_filename):
    with open(index_filename,'r') as f:
        index = json.load(f)
    wd = build_word_dict(index)
    create_wordct_csv(wd)
    create_attr_csvs(index)
