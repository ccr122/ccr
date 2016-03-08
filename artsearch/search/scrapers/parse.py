from num2words import num2words
import re 
#import en
from nltk.stem.snowball import EnglishStemmer

wordre = "[A-Za-z0-9'-]+"

def is_num(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def is_verb(s):
    try:
        s = en.verb.present(s, person=3)
        return True
    except KeyError:
        return False


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
        '''
        w = w.lower()

        if w[0] == "'":
            w = w[1:]
        elif w[-1] == "'":
            w = w[:-1]

        if is_num(w):

        '''

        w = w.lower()             # make all letters lowercase 
        
        if w[0] == "'":              # remove single quotes from beginning/
            w = w[1:]             # end of words in l
        elif w[-1] == "'":
            w = w[:-1]
        
        if is_num(w):                            # wordify single-word numbers
            if len(num2words(int(w)).split(" ")) == 1:
                w = num2words(w)
            #w = num2words(7)
            '''
        elif en.is_noun(w):                  # nouns singular
            plural = en.noun.plural(w)
            w = en.noun.singular(plural)
        elif is_verb(w):    
            w = en.verb.present(w, person=1)  # verbs 1st-person present
        '''
        else:
            w = EnglishStemmer().stem(w)      # stems non-noun/verbs 
            w = w.encode('ascii','ignore')
        if w != '':
            if w not in word_dict:   # build dictionary
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

def create_wordct_csv(word_ct_dict, filename):
    '''
    input:  word_ct_dict {word: ct}
            filename for csv output
    save csv as filename --> ex_id|word
    '''
    with open(filename,'w') as f:
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

ATTR_DICT = {   'title':'exid_title.csv', 
                'date':'exid_date.csv',
                'url':'exid_url.csv'    }

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
