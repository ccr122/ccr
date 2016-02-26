# Convert csv files to SQL databases

# CSV files to convert:
# ex_id_to_ex_date.csv
# ex_id_to_ex_desc.csv  <-- keep this one???
# ex_id_to_ex_desc_parsed.csv
# ex_id_to_ex_title.csv
# ex_id_to_mus_id.csv

import sqlite3
import csv


def create_db(csv_filename, db_filename, table):
    connection_obj = sqlite3.connect(db_filename)
    cursor_obj = connection_obj.cursor()
    create_table_query = "CREATE TABLE {} (col1, col2);".format(table)
    cursor_obj.execute(create_table_query)

    with open(csv_filename,'r') as f:
        f_reader = csv.reader(f)
        line = [(row[0], row[1]) for row in f_reader]
    insert_query = "INSERT INTO {} (col1, col2) VALUES (?, ?);".format(table)
    cursor_obj.executemany(insert_query, line)
    connection_obj.commit()
    connection_obj.close()


if __name__ == "__main__":
    
#    csv_files = ['ex_id_to_ex_date.csv', 'ex_id_to_ex_desc.csv', 'ex_id_to_ex_desc_parsed.csv', 
 #   'ex_id_to_ex_title.csv', 'ex_id_to_mus_id.csv']

#    db_files = ['ex_id_to_ex_date.db', 'ex_id_to_ex_desc.db', 'ex_id_to_ex_desc_parsed.db', 
 #   'ex_id_to_ex_title.db', 'ex_id_to_mus_id.db']

  #  table_names = ['t_date', 't_desc', 't_desc_parsed', 't_title', 't_mus_id']

   # for i in range(len(csv_files)):
    #    create_db(csv_files[i], db_files[i], table_names[i])

    create_db('ex_id_to_ex_date.csv', 'ex_id_to_ex_date.db', 't_date')
#    create_db('ex_id_to_ex_desc.csv', 'ex_id_to_ex_desc.db', 't_desc')
    create_db('ex_id_to_ex_desc_parsed.csv', 'ex_id_to_ex_desc_parsed.db', 't_desc_parsed')
    create_db('ex_id_to_ex_title.csv', 'ex_id_to_ex_title.db', 't_title')
    create_db('ex_id_to_mus_id.csv', 'ex_id_to_mus_id.db', 't_mus_id')