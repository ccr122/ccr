# CS122: Course Search Engine Part 1
#
# Cynthia Mao
#

import re
#import util
import bs4
import queue
import json
import sys
import csv
import urllib.parse

INDEX_IGNORE = set(['a',  'also',  'an',  'and',  'are',  'as',  'at',  'be',
                    'but',  'by',  'depict',  'depicts',  'exhibition',  'exhibitions',
                    'for',  'from',  'he',  'how',  'i',  'ii',  'iii',  'in',  'include',
                    'is',  'not',  'of',  'on',  'or',  'portray',  'portrays',  'she',
                    'so',  'social',  'something',  'such',  'than',  'that',  'the',
                    'their',  'this',  'through',  'to',  'topics',  'we',  'were',
                    'which',  'will',  'with',  'work',  'works',  'yet'])


### YOUR FUNCTIONS HERE

def go(num_pages_to_crawl, course_map_filename, index_filename):
    '''
    Crawl the college catalog and generates a CSV file with an index.

    Inputs:
        num_pages_to_crawl: the number of pages to process during the crawl
        course_map_filename: the name of a JSON file that contains the mapping
          course codes to course identifiers
        index_filename: the name for the CSV of the index.

    Outputs: 
        CSV file of the index index.
    '''

    starting_url = "http://www.nationalmuseumofmexicanart.org/content/exhibitions"
    limiting_domain = "nationalmuseumofmexicanart.org/exhibits"
    LEN_LIMIT = len(limiting_domain)

    index = {}
 #   visited = []
 #   count = 0

 #   urls_queue = queue.Queue()
  #  urls_queue.put(starting_url)

   # urls_set = set([starting_url])
    urls_list = []

    traverse_links(starting_url, urls_list, limiting_domain)
 #   make_csv(index, index_filename)



def traverse_links(starting_url, urls_list, limiting_domain):
 #   url = urls_queue.get()
  #  urls_set.remove(url)
#    visited.append(url)
    
    request = get_request(starting_url)
    string = read_request(request)
    soup = bs4.BeautifulSoup(string, 'html5lib')
    
    all_urls = soup.find_all('a', href = True)
    for each_url in all_urls:
        each_url = each_url['href']
        if is_exhibit(each_url, limiting_domain):
            urls_list.append(each_url)

    # visit exhibit page and find info on it
    for each_url in urls_list:
        exhibit_request = get_request(each_url)
        exhibit_string = read_request(exhibit_request)
        exhibit_soup = bs4.BeautifulSoup(string, 'html5lib')
        index_exhibit(exhibit_soup, index)
    
    return index

def index_exhibit(soup, index):
    contains_exhibit_name = soup.find_all('title')
    contains_exhibit_name = contains_exhibit_name[0].string.split(' | ')
    exhibit_name = contains_exhibit_name[0]
    museum_name = contains_exhibit_name[1]
    if exhibit_name not in index:
        index[exhibit_name] = {'museum': museum_name, 'contents': []}

    all_list = soup.find_all('div', class_ = 'field-type-text-with-summary')
    for item in all_list:
        if item.string:
            for word in item.string.split(' '):
                new_word = is_word(word.lower())
                if new_word:
                    if new_word not in index[exhibit_name]['contents']:
                        index[exhibit_name]['contents'].append(new_word)


def is_exhibit(url, limiting_domain):
    if not url:
        return False

 #   if isinstance(url, bytes):
  #      url = url.decode(encoding='UTF-8')

    if "mailto:" in url:
        return False

    if "@" in url:
        return False

    parsed_url =  urllib.parse.urlparse(url)
    if parsed_url.scheme != "http" and parsed_url.scheme != "https":
        return False

    if parsed_url.netloc == 'nationalmuseumofmexicanart.org' or \
    parsed_url.netloc == 'www.nationalmuseumofmexicanart.org':  # generalize?
        if parsed_url.path[:8] == '/exhibit':
            return True

    if parsed_url.fragment:
        return False

    if parsed_url.query:
        return False

 #   if parsed_url.path[:8] != '/exhibit': # generalize? use limiting_domain
  #      return False

  #  else:
   #     return True









def is_word(word_to_check):
    '''
    Determines if word_to_check begins with a letter, contains letters and numbers

    Inputs:
      word_to_check: string to check

    Outputs:
      string
    '''
    exp = re.compile('^[a-z][a-z0-9]*')
    match = re.match(exp, word_to_check)
    if match:
        match = match.group()
        if match not in INDEX_IGNORE:
            return match


def make_csv(index, filename):
    '''
    Creates csv file and writes index

    Inputs:
      index: index mapping words to course identifiers
      filename: name of CSV file
    '''
    with open(filename, 'w') as f:
        for k,v in index.items():
            for each_id in v:
                line = str(each_id) + '|' + k + '\n'
                f.write(line)



def get_request(url):
    '''
    Open a connection to the specified URL and if successful
    read the data.

    Inputs:
        url: must be an absolute URL
    
    Outputs: 
        request object or None

    Examples:
        get_request("http://www.cs.uchicago.edu")
    '''

    if is_absolute_url(url):
        try:
            r = requests.get(url)
            if r.status_code == 404 or r.status_code == 403:
                r = None
        except:
            # fail on any kind of error
            r = None
    else:
        r = None

    return r


def read_request(request):
    '''
    Return data from request object.  Returns result or "" if the read
    fails..
    '''

    try:
        return request.text.encode('iso-8859-1')
    except:
        print("read failed: " + request.url)
        return ""

def is_absolute_url(url):
    '''
    Is url an absolute URL?
    '''
    if len(url) == 0:
        return False
    return len(urllib.parse.urlparse(url).netloc) != 0






'''

if __name__ == "__main__":
    usage = "python3 crawl.py <number of pages to crawl>"
    args_len = len(sys.argv)
    course_map_filename = "course_map.json"
    index_filename = "catalog_index.csv"
    if args_len == 1:
        num_pages_to_crawl = 1000
    elif args_len == 2:
        try:
            num_pages_to_crawl = int(sys.argv[1])
        except ValueError:
            print(usage)
            sys.exit(0)
    else:
        print(usage)    
        sys.exit(0)


    go(num_pages_to_crawl, course_map_filename, index_filename)



'''
