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

#d = []
#for museum in indexes:
 #   d.append(museum)

for museum in indexes:
    for exhibit in museum:
        make_csv(museum, exhibit, 'title', 'ex_id_to_ex_title.csv')

make_csv(indexes, 'title', 'ex_id_to_ex_title.csv')
make_csv(indexes, 'date', 'ex_id_to_ex_date.csv')
make_csv(indexes, 'desc', 'ex_id_to_ex_desc.csv')

def make_csv(indexes, var_of_interest, filename):
    with open(filename, 'w') as f:
        for museum in indexes:
            for exhibit in museum:
                var_value = museum[exhibit][var_of_interest]
                if var_of_interest == 'desc':
                    var_value = parse_desc(var_value)
                line = '{},{}\n'.format(str(exhibit), str(var_value))
                f.write(line)

def parse_desc(var_value):