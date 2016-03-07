# scrape_met.py

import requests
import bs4
import util
import re

DATE_PATTERN = '([\w, ]*)\&ndash\;([\w, ]*)'
IGNORABLE = 'media_feed=[1-9]'

'''ARTIC
div class="field-items"><div class="field-item even" property="content:encoded"
 class="field field-name-field-exhibition-room field-type-text field-label-hidden"

 h1 id="page-title"
'''


def get_new_urls(soup,here,urls,limiting_domain):

    for link in soup.find_all('a', href=True):
        if len(urls)>=20:
            return urls

        u = util.convert_if_relative_url(here, link['href'])
        u = util.remove_fragment(u)
        if ((limiting_domain in u) and (u not in urls) 
            and (re.search(IGNORABLE,u)==None)):
            urls+=[u]
    return urls

def artic_parser(minfo, soup, u, exhibition_no):
    body_soup = soup.find('div',class_='field-item even', property="content:encoded")
    if body_soup ==None:
        return exhibition_no
    exhibition_no +=1
    exhibition_code = str(exhibition_no)
    if len(exhibition_code) <2:
        exhibition_code = "0"+exhibition_code
    exhibition_code = "001"+exhibition_code
    title_soup = soup.find('h1', id="page-title")
    date_soup = soup.find('div',class_ = "field-item even")
    e = {   'title' :title_soup.get_text(),
            'url'   :u,
            'desc'  :body_soup.get_text(),
            'date'  :date_soup.get_text()
    }

#    print("\n")
 #   for i in range(0,len(e['desc']),70):
  #      print("\t"+e['desc'][i:min(i+70,len(e['desc']))])
   # print("\n")
    #print (e['date']+"\n\n")

    minfo[exhibition_code] = e
    return exhibition_no


        
def MCA_parser(minfo,soup,u,exhibition_no):
    '''
    h1 class="title
     div class="bg_white"
     page-header__sub
    '''
    regex_url = "https:\/\/mcachicago.org\/Exhibitions\/201[0-6]\/"
    if re.search(regex_url,u)==None:
      #  print("\t\t No.")
        return exhibition_no
    title_soup = soup.find('h1',class_="title")
  #  print("\t"+str(title_soup.get_text()))
    bodyish_soup = soup.find_all('div',class_='bg_white')
    exhibition_no+=1
    exhibition_code=str(exhibition_no)
    if len(exhibition_code)<2:
        exhibition_code = '0'+exhibition_code
    exhibition_code = '002'+exhibition_code

    dates_raw = soup.find_all('p',class_='dates')
    date = dates_raw[0].get_text()
    desc_raw = soup.find_all('div',class_='body')
    desc = desc_raw[0].get_text()

    e = {   'title' : title_soup.get_text(),
            'url'   : u, 
            'desc'  : desc,
            'date'  : date
    }
    minfo[exhibition_code] = e

    #
   # print("\n")
    #

    return exhibition_no
    

ARTIC = {   'starting_url'      : "http://www.artic.edu/exhibitions",
            'limiting_domain'   : "http://www.artic.edu/exhibition",
            'museum_id'         : '001',
            'parser'            : artic_parser
        }

MCA =    {  'museum_id'         : '002',
            'limiting_domain'   : 'https://mcachicago.org/Exhibitions',
            'starting_url'      : 'https://mcachicago.org/Exhibitions',
            'parser'            : MCA_parser
        }

MUSEUMS = [ARTIC, MCA]

def scrape(MUSEUMS):
    index = {}
    for m in MUSEUMS:
        ##
        print("___________\n")
        for s in m:
            print (s+"\t:\t"+str(m[s]))
        print("\n")
        ##
        minfo = {}
        exhibition_no = 0
        index[m['museum_id']] = minfo
        to_visit = []
        urls = [m['starting_url']]
        for u in urls:
            ##
            print (" " + str(u))
            ##
            r = util.get_request(u)
            if r == None:
                continue
            soup = bs4.BeautifulSoup(r.text,'html5lib')
            exhibition_no = m['parser'](minfo,soup,u, exhibition_no)
            urls = get_new_urls(soup,u,urls, m['limiting_domain'])

        #minfo['urls'] = urls
    print("_____SCRAPING_COMPLETE_____________________________________\n")
    return index

