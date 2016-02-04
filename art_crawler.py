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

def go(starting_urls, museum_id, limiting_domain):
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
                    abs_url = make_absolute_url(limiting_domain, url)
                    if abs_url not in to_visit:
                        to_visit.append(abs_url)
    count = 1
    for ex in to_visit:
        rex = requests.get(ex)
        exsoup = bs4.BeautifulSoup(rex.text, 'html5lib')
        exhibit_id = make_exhibit_id(count)
        title_text = exsoup.h1.string
        dates = find_date(exsoup)
        description = find_description(exsoup)
        index[museum_id][exhibit_id] = {'title': title_text, 'desc': description, \
        'date': dates}
        count += 1
    return index


def find_description(soup):
    if soup.find('meta', attrs = {'name': 'description'}):
        desc_string = soup.find('meta', attrs = {'name': 'description'})['content']
    elif soup.find('div', class_ = 'panel-pane pane-custom pane-3'):
        contains_desc = soup.find('div', class_ = 'panel-pane pane-custom pane-3').find_all('p')
        desc_string = ''
        for d in contains_desc:
            if d.get_text():
                desc_string += d.get_text()
            else:
                break
    return desc_string


def find_date(soup):
    if soup.find('span', class_ = 'date-display-start'):
        start_date = soup.find('span', class_ = 'date-display-start').string
        end_date = soup.find('span', class_ = 'date-display-end').string
        return [start_date, end_date]
    elif soup.find('div', id = 'dates'):
        start_end_date = soup.find('div', id = 'dates').find('h3').string
        return start_end_date
    elif soup.find('div', id = 'mainTitle'):
        start_end_date = soup.find('div', id = 'mainTitle').find('p').string
        return start_end_date

def make_exhibit_id(count):
    excount = str(count)
    zeroes = EXHIBIT_LEN - len(excount)
    excount = str(0)*zeroes + excount
    ex_id = DEYOUNG + excount
    return ex_id

def make_absolute_url(limiting_domain, relative_url):
    abs_url = limiting_domain + relative_url
    return abs_url

if __name__ == "__main__":
    starting_deyoung = ["http://deyoung.famsf.org/exhibitions/current", \
    "http://deyoung.famsf.org/exhibitions/upcoming"]
    limiting_deyoung = "http://deyoung.famsf.org"
    starting_legion = ["http://legionofhonor.famsf.org/exhibitions/current", \
    "http://legionofhonor.famsf.org/exhibitions/upcoming"]
    limiting_legion = "http://legionofhonor.famsf.org"
    
    deyoung = go(starting_deyoung, DEYOUNG, limiting_deyoung)
    legion = go(starting_legion, LEGION, limiting_legion)

    print(deyoung, legion)
