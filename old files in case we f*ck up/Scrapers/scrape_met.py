# scrape_met.py
# usage: run scrape_met.py
#        scrape_met()
# returns dictionary

import requests
import bs4
import util
import re

def find_exhibit_urls(limiters, page, exhibit_urls):
    r = requests.get(page)
    soup = bs4.BeautifulSoup(r.text, "html5lib")
    for link in soup.find_all('a', href=True):
        u = util.convert_if_relative_url(page, link['href'])
        u = util.remove_fragment(u)
        if (limiters[0] in u) or (limiters[1] in u):
            if u not in exhibit_urls:
                exhibit_urls += [u]

def get_exhibit_info(soup, museum_dict, exhibit_id):
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
#    print("title is " + title)

    desc_code = soup.find('div', class_="text-box cleared").get_text()
    museum_dict[exhibit_id]['desc'] = desc_code.strip()

    date_code = soup.find('h4', class_="date").get_text()
    date_code = date_code.strip()
    museum_dict[exhibit_id]['date'] = date_code

def scrape_met():
    limiters = ["http://www.metmuseum.org/exhibitions/listings/",
                "http://www.metmuseum.org/en/exhibitions/listings/"]
    pages = ["http://www.metmuseum.org/exhibitions/current-exhibitions",
             "http://www.metmuseum.org/exhibitions/upcoming-exhibitions"]

    exhibit_urls = []
    for page in pages:
        find_exhibit_urls(limiters, page, exhibit_urls)

    museum_id = '003'

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