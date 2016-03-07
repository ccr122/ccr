# scrape_met_moma.py

import requests
import bs4
import util
import re

def crawl_met(limiters, page, exhibit_urls):
    r = requests.get(page)
    soup = bs4.BeautifulSoup(r.text, "html5lib")
    for link in soup.find_all('a', href=True):
        u = util.convert_if_relative_url(page, link['href'])
        u = util.remove_fragment(u)
        if (limiters[0] in u) or (limiters[1] in u):
            if u not in exhibit_urls:
                exhibit_urls += [u]

def build_met(soup, museum_dict, exhibit_id):
    # does not preserve italics... need to figure out how to change
    museum_dict[exhibit_id] = {}
    title_code = soup.find('div', class_="text-box first cleared")
    title = title_code.find('h1').get_text()
    title = title.strip()
    subtitle = title_code.find('h2').get_text()
    subtitle = subtitle.strip()
    if len(subtitle) != 0:
        title += ": " + subtitle
    museum_dict[exhibit_id]['title'] = title
    # print("title is " + title)

    desc_code = soup.find('div', class_="text-box cleared").get_text()
    museum_dict[exhibit_id]['desc'] = desc_code.strip()

    date_code = soup.find('h4', class_="date").get_text()
    date_code = date_code.strip()
    museum_dict[exhibit_id]['date'] = date_code
    
def crawl_moma(limiter, page, exhibit_urls):
        r = requests.get(page)
        soup = bs4.BeautifulSoup(r.text, "html5lib")
        for link in soup.find_all('a', href=True):
            u = util.convert_if_relative_url(page, link['href'])
            u = util.remove_fragment(u)
            if limiter in u:
                if u not in exhibit_urls:
                    exhibit_urls += [u]
                    
def build_moma(soup, museum_dict, exhibit_id):
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

scrape_dict = { '003':{ 'limiter':  ["http://www.metmuseum.org/exhibitions/listings/",
                                    "http://www.metmuseum.org/en/exhibitions/listings/"]
                        'page':     ["http://www.metmuseum.org/exhibitions/current-exhibitions",
                                    "http://www.metmuseum.org/exhibitions/upcoming-exhibitions"]
                        'crawler':  crawl_met,
                        'info':     build_met}
                '004':{ 'limiter':  'http://www.moma.org/calendar/exhibitions/',
                        'page':     'http://www.moma.org/calendar/exhibitions',
                        'crawler':  crawl_moma,
                        'info':     build_moma}

def scrape():
    index = {}
    for museum_id in scrape_dict:
        limiter = scrape_dict[museum_id]['limiter']
        page = scrape_dict[museum_id]['page']
        exhibit_urls = []
        find_exhibit_urls(limiter, page, exhibit_urls)
        index[museum_id] = {}
        exhibit_id = museum_id + '01'
    
        for link in exhibit_urls:
            r = requests.get(link)
            soup = bs4.BeautifulSoup(r.text,"html5lib")
            scrape_dict[museum]['fcn'](soup, index[museum_id], exhibit_id)
            index[museum_id][exhibit_id]['url'] = link
            exhibit_id = '00' + str(int(exhibit_id) + 1)
    
    return index
    