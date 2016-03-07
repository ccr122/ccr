from num2words import num2words
import re 
import en
from nltk.stem.snowball import EnglishStemmer

wordre = "[a-z0-9'-]+"

def is_num(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def is_verb(s):
    try:
        l[i] = en.verb.present(l[i], person=3)
        return True
    except KeyError:
        return False


def str_to_dict(s):
    '''
    input:  s string
    output: dictionary {word: count}
    '''
    word_dict = {}
    l = re.findall(wordre, s)
    for i in range(len(l)):

        l[i] = l[i].lower()             # make all letters lowercase 
        
        if l[i][0] == "'":              # remove single quotes from beginning/
            l[i] = l[i][1:]             # end of words in l
        elif l[i][-1] == "'":
            l[i] = l[i][:-1]

        if is_num(l[i]):                            # wordify single-word numbers
            if len(num2words(int(l[i])).split(" ")) == 1:
                l[i] = num2words(l[i])
        elif en.is_noun(l[i]):                      # nouns singular
            plural = en.plural(l[i])
            l[i] = en.singular(plural)
        elif is_verb(l[i]):    
            l[i] = en.verb.present(l[i], person=3)  # verbs 3rd-person present
        else:
            l[i] = EnglishStemmer().stem(l[i])      # stems non-noun/verbs 
        
        if l[i] != '':
            if l[i] not in word_dict:   # build dictionary
                word_dict[l[i]] = 1
            else:
                word_dict[l[i]] += 1

    return word_dict

def build_word_dict(index):
    
    input:  index (the dict passed from scraping)
    output: word_dict {word: ct}
    
    word_dict = {}
    for museum_id in index:
        word_dict[museum_id] = {}
        for ex_id in index[museum_id]:
            word_dict[museum_id][ex_id] = {}
            words = index[museum_id][ex_id]['title'] 
            words += index[museum_id[ex_id]['desc']
            word_dict[museum_id][ex_id] = str_to_dict(words)
    
    return word_dict


def create_wordct_csv(word_ct_dict, filename):
    '''
    input:  word_ct_dict {word: ct}
            filename for csv output
    save csv as filename --> ex_id|word
    '''
    with open(filename) as f:
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

ATTR_DICT = {   'title':'csvs/exid_title.csv', 
                'date':'csvs/exid_date.csv',
                'url':'csvs/exid_url.csv'    }

def create_attr_csvs(index):
    for attr in ATTR_DICT:
        with open(ATTR_DICT[attr]) as f:
            line = 'ex_id|' + attr + '\n'
            f.write(line)
            for museum_id in index:
                for ex_id in index[museum_id]:
                    line = '{}|{}\n'.format(str(ex_id), \
                        str(index[museum_id][ex_id][attr]))
                    f.write(line)   
