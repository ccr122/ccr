# run all scrape files to get 6 museum indexes
# create 5 csv files:
# - exhibit ID to museum ID: 
# - exhibit ID to exhibit description text (unparsed): ex_id_to_ex_desc.csv
# - exhibit ID to exhibit date: ex_id_to_ex_date.csv
# - exhibit ID to exhibit title: ex_id_to_ex_title.csv
# - exhibit ID to exhibit title and description text (parsed)

# museum ids:   {ART INSTITUTE OF CHICAGO: 001,
#                MUSEUM OF CONTEMPORARY ART: 002,
#                METROPOLITAN MUSEUM OF ART: 003,
#                MUSEUM OF MODERN ART: 004,
#                DEYOUNG: 005,
#                LEGION OF HONOR: 006}


import scrape_artic_mca
import scrape_met
import scrape_moma
import scrape_deyoung_legion
import csv
import re

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
                    'experience', 'feature', 'features', 'foundation',
                    'first', 'for',  'from', 'funding', 'go', 'goes', 
                    'gone', 'had', 'have', 
                    'has', 'he', 'her', 'hers', 
                    'him', 'his',
                    'how', 'i', 'ii', 'iii', 'idea', 'in',  
                    'include', 
                    'institute', 'interpret', 'interpretation', 'into',
                    'is', 'it', 'just', 'many', 'meaning', 'modern', 'more', 'motif', 
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


def make_csv(indexes, var_of_interest, filename):
    with open(filename, 'w') as f:
        i = 1
        for museum in indexes:
            if i == 1:
                line = 'ex_id,' + var_of_interest + '\n'
                f.write(line)
                i = 2
            for exhibit in museum:
                var_value = museum[exhibit][var_of_interest]
                line = '{},{}\n'.format(str(exhibit), str(var_value))
                f.write(line)

def make_date_csv(indexes, filename):
    with open(filename, 'w') as f:
        i = 1
        for museum in indexes:
            if i == 1:
                line = 'ex_id,date\n'
                f.write(line)
                i = 2
            for exhibit in museum:
                rawdate = museum[exhibit]['date']
                if type(rawdate) != list:
                  #  date = rawdate.split('–')
                    date = [rawdate]
                line = '{},{}\n'.format(str(exhibit), date)
                f.write(line)

def make_parsed_desc_csv(indexes, filename):
    with open(filename, 'w') as f:
        i = 1
        for museum in indexes:
            if i == 1:
                line = 'ex_id,word\n'
                f.write(line)
                i = 2
                continue
            for exhibit in museum:
                unparsed = museum[exhibit]['desc']
                parsed = parse_desc(unparsed)
                for word in parsed:
                    line = '{},{}\n'.format(str(exhibit), word)
                    f.write(line)

def make_ex_mus_id_csv(indexes, filename):
    with open(filename, 'w') as f:
        i = 1
        for museum in indexes:
            if i == 1:
                line = 'ex_id,mus_id\n'
                f.write(line)
                i = 2
            for exhibit in museum:
                museum_id = exhibit[0:3]
                line = '{},{}\n'.format(str(exhibit), str(museum_id))
                f.write(line)

def parse_desc(unparsed_desc):
    parsed = []
    unparsed = unparsed_desc.split(' ')
    for word in unparsed:
        word = word.lower()
        new_word = is_word(word)
        if new_word:
            parsed.append(new_word)
    return parsed

def is_word(word_to_check):
    exp = re.compile("^[a-z][a-z-']*")
    match = re.match(exp, word_to_check)
    if match:
        match = match.group()
        if match not in INDEX_IGNORE:
            return match


if __name__ == "__main__":
    
    # Create all museum indexes

    indexes = []

    # ART INSTITUTE OF CHICAGO

    index_artic_mca = scrape_artic_mca.scrape(scrape_artic_mca.MUSEUMS)  # a dictionary of 2 dictionaries
    index_artic = index_artic_mca['001']
    indexes.append(index_artic)

    # MUSEUM OF CONTEMPORARY ART (CHICAGO)
    index_mca = index_artic_mca['002']
    indexes.append(index_mca)

    # METROPOLITAN MUSEUM OF ART

    index_met = scrape_met.scrape_met()
    indexes.append(index_met['003'])

    # MUSEUM OF MODERN ART (NEW YORK)

    index_moma = scrape_moma.scrape_moma()
    indexes.append(index_moma['004'])

    # DEYOUNG

    starting_deyoung = ["http://deyoung.famsf.org/exhibitions/current", \
    "http://deyoung.famsf.org/exhibitions/upcoming"]
    limiting_deyoung = "http://deyoung.famsf.org"
    DEYOUNG = '005'
    index_deyoung = scrape_deyoung_legion.go(starting_deyoung, DEYOUNG, limiting_deyoung)
    indexes.append(index_deyoung['005'])

    # LEGION OF HONOR

    starting_legion = ["http://legionofhonor.famsf.org/exhibitions/current", \
    "http://legionofhonor.famsf.org/exhibitions/upcoming"]
    limiting_legion = "http://legionofhonor.famsf.org"
    LEGION = '006'
    index_legion = scrape_deyoung_legion.go(starting_legion, LEGION, limiting_legion)
    indexes.append(index_legion['006'])

    # Create csv tables

    make_parsed_desc_csv(indexes, 'ex_id_to_ex_desc_parsed.csv')
    make_csv(indexes, 'title', 'ex_id_to_ex_title.csv')
    make_date_csv(indexes, 'ex_id_to_ex_date.csv')
    make_csv(indexes, 'desc', 'ex_id_to_ex_desc.csv')
    make_ex_mus_id_csv(indexes, 'ex_id_to_mus_id.csv')