# scrape_new_moma.py

import requests
import bs4
import util
import re

scrape_dict = { '003':{ 'limiter':  "http://www.newmuseum.org/exhibitions/view/",
                        'page':     ["http://www.newmuseum.org/exhibitions/current",
                                    "http://www.newmuseum.org/exhibitions/upcoming"],
                        'crawler':  crawl,
                        'info':     build_new},
                '004':{ 'limiter':  'http://www.moma.org/calendar/exhibitions/',
                        'page':     ['http://www.moma.org/calendar/exhibitions'],
                        'crawler':  crawl,
                        'info':     build_moma}}

def crawl(limiter, exhibit_urls, u):
    if  (limiter in u) and (u not in exhibit_urls):
        exhibit_urls += [u]

def build_new(soup, museum_dict, exhibit_id):
    title = soup.find('h3', style='color: #fff;').get_text()
    museum_dict[exhibit_id]['title'] = title.strip()

    desc = soup.find('div', class_="body").get_text()
    museum_dict[exhibit_id]['desc'] = desc.strip()

    date = soup.find('p', class_="date-range").get_text()
    museum_dict[exhibit_id]['date'] = date.strip()
                   
def build_moma(soup, museum_dict, exhibit_id):
    # does not preserve italics
    museum_dict[exhibit_id] = {}
    title = soup.find('h1', class_="page-header__title").get_text()
    museum_dict[exhibit_id]['title'] = title.strip()

    desc = soup.find('div', class_="mde-column__section").get_text()
    museum_dict[exhibit_id]['desc'] = desc.strip()

    date = soup.find('h2', class_="page-header__subheading--narrow").get_text()
    museum_dict[exhibit_id]['date'] = date.strip()

def scrape():
    index = {}
    for museum_id in scrape_dict:
        limiter = scrape_dict[museum_id]['limiter']
        pages = scrape_dict[museum_id]['page']
        exhibit_urls = []
        for page in pages:
            r = requests.get(page)
            soup = bs4.BeautifulSoup(r.text, "html5lib")
            for link in soup.find_all('a', href=True):
                u = util.convert_if_relative_url(page, link['href'])
                u = util.remove_fragment(u)
                scrape_dict[museum_id]['crawler'](limiter, exhibit_urls, u)

        index[museum_id] = {}
        exhibit_id = museum_id + '01'

        for link in exhibit_urls:
            r = requests.get(link)
            soup = bs4.BeautifulSoup(r.text,"html5lib")
            index[museum_id][exhibit_id] = {}
            scrape_dict[museum_id]['info'](soup, index[museum_id], exhibit_id)
            index[museum_id][exhibit_id]['url'] = link
            exhibit_id = '00' + str(int(exhibit_id) + 1)
    
    return index
    