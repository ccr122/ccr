import re
import util
import bs4
import queue
import json
import sys
import csv
import requests

#INDEX_IGNORE = set(['a',  'also',  'an',  'and',  'are', 'as',  'at',  'be',
 #                   'but',  'by',  'course',  'for',  'from',  'how', 'i',
  #                  'ii',  'iii',  'in',  'include',  'is',  'not',  'of',
   #                 'on',  'or',  's',  'sequence',  'so',  'social',  'students',
    #                'such',  'that',  'the',  'their',  'this',  'through',  'to',
     #               'topics',  'units', 'we', 'were', 'which', 'will', 'with', 'yet'])
EXHIBIT_LEN = 2
DEYOUNG = '005'
LEGION = '006'

### YOUR FUNCTIONS HERE

def go(starting_urls, museum_id):
    index = {museum_id: {}}
    to_visit = []

    for s in starting_urls:
        r = requests.get(s)
        soup = bs4.BeautifulSoup(r.text, 'html5lib')
        all_urls = soup.find_all('a', href = True)
        for u in all_urls:
            url = u['href']
            exp = re.compile('/exhibitions/[a-z]+')
            if exp.match(url):
                url_match = exp.match(url).group()
                if url_match != '/exhibitions/current' and \
                url_match != '/exhibitions/upcoming' and \
                url_match != '/exhibitions/archive':
                    abs_url = make_absolute_url(s, url)
                    if abs_url not in to_visit:
                        to_visit.append(abs_url)
    count = 1
    for ex in to_visit:
        rex = requests.get(ex)
        exsoup = bs4.BeautifulSoup(rex.text, 'html5lib')
        exhibit_id = make_exhibit_id(count)
        title_text = exsoup.h1.string  # why is it getting the h1 of soup and not exsoup?
        start, end = find_date(exsoup)  # not working?
        description = find_description(exsoup)  # not working?
        index[museum_id][exhibit_id] = {'title': title_text, 'desc': '', \
        'date': []}
        count += 1
    return to_visit, index


def find_description(soup):
    contains_desc = soup.find_all('div', class_ = 'field-name-body')[0].find_all('p')
    desc_string = ''
    for d in contains_desc:
        if d.get_text():
            desc_string += d.get_text()
        else:
            break
    return desc_string

def find_date(soup):
    start_date = soup.find('div', class_ = 'date-display-start').string  # why not working?
    end_date = soup.find('div', class_ = 'date-display-end').string  # why not working?
    return start_date, end_date

def make_exhibit_id(count):
    excount = str(count)
    zeroes = EXHIBIT_LEN - len(excount)
    excount = str(0)*zeroes + excount
    ex_id = DEYOUNG + excount
    return ex_id

def make_absolute_url(page_url, relative_url):
    abs_url = page_url + relative_url
    return abs_url

if __name__ == "__main__":
    starting_deyoung = ["http://deyoung.famsf.org/exhibitions/current", \
    "http://deyoung.famsf.org/exhibitions/upcoming"]
    starting_legion = ["http://legionofhonor.famsf.org/exhibitions/current", \
    "http://legionofhonor.famsf.org/exhibitions/upcoming"]
    
    go(starting_deyoung, DEYOUNG)
    go(starting_legion, LEGION)
