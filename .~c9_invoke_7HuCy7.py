from num2Words import num2Words
import re 

wordre = "[A-Za-z0-9'-]+"

INDEX_IGNORE = set(['a', 'about', 'affect', 'affects', 'all', 'among',
                    'approximately' 'also', 'after', 'an',  'and',  
                    'are', 'art', 'artist', 'artists', "artist's", 'arts', 'as',  'at', 
                    'be', 'been', 'between', 'both', 'bring',
                    'but',  'by', 'collect', 'collected', 'collection', 
                    'contribute', 'contributed', 'come',
                    'composition', 'display', 'displays', 
                    'early', 'effect', 'effects', 
                    'evoke', 'evoked', 'exhibit',
                    'exhibits', 'exhibition', 'exhibitions',
                    'experience', 'feature', 'features',
                    'first', 'for',  'from', 'funding', 'go', 'goes', 
                    'gone', 'had', 'have', 
                    'has', 'he', 'her', 'hers', 
                    'how', 'i', 'ii', 'iii', 'idea', 'in',  
                    'how', 'i', 'ii', 'iii', 'idea', 'in',  
                    'include', 
                    'institute', 'interpret', 'interpretation', 'into',
                    'is', 'it', 'just', 'many', 'meaning', 'more', 'motif', 
                    'museum', 'not', 'of',
                    'on', 'only',  'or', 'other', 'over', 
                    'period', 'piece', 'pieces', 
                    'presentation', 
                    'second', 'see', 'significance', 'significant', 
                    'so', 'society', 'span', 
                    'special', 
                    'sponsor', 
                    'sponsors', 'sponsored', 'study',
                    'such', 'support', 'than', 
                    'that',  'the',  'their', 'third',
                    'this', 'the', 'their', 'they', 'through',  'to', 'trust',
                    'was', 'we', 'well', 'were', 'when', 'where', 
                    'which', 'who', 'will', 'with', 'would', 
                    'work', 'works', 'world', 'view',
                    'until', 'visit', 'yet'])

def str_to_dict(s):
    '''
    input: string
    output: dictionary {word: count}
    '''
    word_dict = {}
    l = re.findall(wordre, s)
    for i in range(len(l)):
        if l[i] can be int:             # turn numbers into words
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
        
    