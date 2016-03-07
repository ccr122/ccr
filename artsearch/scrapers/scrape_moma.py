# scrape_moma.py 
# usage: run scrape_moma.py
#        scrape_moma()
# returns dictionary 

import requests
import bs4
import util
import re

def find_exhibit_urls(limiter, page, exhibit_urls):
        r = requests.get(page)
        soup = bs4.BeautifulSoup(r.text, "html5lib")
        for link in soup.find_all('a', href=True):
            u = util.convert_if_relative_url(page, link['href'])
            u = util.remove_fragment(u)
            if limiter in u:
                if u not in exhibit_urls:
                    exhibit_urls += [u]

def get_exhibit_info(soup, museum_dict, exhibit_id):
    # does not preserve italics
    museum_dict[exhibit_id] = {}
    title_code = soup.find('h1', class_="page-header__title")
    title = title_code.get_text()
    title = title.strip()
    museum_dict[exhibit_id]['title'] = title

    desc_code = soup.find('div', class_="mde-column__section").get_text()
    museum_dict[exhibit_id]['desc'] = desc_code.strip()

    date_code = soup.find('h2', class_="page-header__subheading--narrow").get_text()
    museum_dict[exhibit_id]['date'] = date_code.strip()

def scrape_moma():
    limiter = "http://www.moma.org/calendar/exhibitions/"
    page = "http://www.moma.org/calendar/exhibitions"
    exhibit_urls = []
    find_exhibit_urls(limiter, page, exhibit_urls)

    museum_id = '004'
    index = {}
    index[museum_id] = {}
    exhibit_id = museum_id + '01'

    for link in exhibit_urls:
        r = requests.get(link)
        soup = bs4.BeautifulSoup(r.text,"html5lib")
        get_exhibit_info(soup, index[museum_id], exhibit_id)
        index[museum_id][exhibit_id]['url'] = link
        exhibit_id = '00' + str(int(exhibit_id) + 1)

    return index 

