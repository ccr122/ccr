# scrape_new_moma.py

import requests
import bs4
import util
import re

def crawl(limiter, exhibit_urls, u, restr):
    if  (limiter in u) and (u not in exhibit_urls) and \
        (u not in restr) and (restricted_string not in u):
        exhibit_urls += [u]
        print(u)

restricted_string = "http://www.artic.edu/exhibitions?qt-media_feed"

def build_artic(soup, museum_dict, exhibit_id):
    title = soup.find('title').get_text().strip()
    title = title[:-31]
    museum_dict[exhibit_id]['title'] = title 

    desc = soup.find('div',class_='field-item even', property="content:encoded").get_text().strip()
    museum_dict[exhibit_id]['desc'] = desc

    date = soup.find('div',class_ = "field-item even").get_text().strip()
    museum_dict[exhibit_id]['date'] = date

def build_mca(soup, museum_dict, exhibit_id):
    title = soup.find('title').get_text().strip()
    title = title[6:]
    museum_dict[exhibit_id]['title'] = title 

    desc = soup.find('div', class_="bg_white").get_text().strip()
    museum_dict[exhibit_id]['desc'] = desc

    '''
    date = soup.find('p', class_='dates').string
    date = soup.find_all('p', class_='dates')
    date = date[0].get_text().strip()
    print(date)
    museum_dict[exhibit_id]['date'] = date
    '''

    museum_dict[exhibit_id]['date'] = 'COME SEE IT'

def build_new(soup, museum_dict, exhibit_id):
    title = soup.find('h3', style='color: #fff;').get_text().strip()
    museum_dict[exhibit_id]['title'] = title

    desc = soup.find('div', class_="body").get_text().strip()
    museum_dict[exhibit_id]['desc'] = desc

    date = soup.find('p', class_="date-range").get_text().strip()
    museum_dict[exhibit_id]['date'] = date
                   
def build_moma(soup, museum_dict, exhibit_id):
    title = soup.find('h1', class_="page-header__title").get_text().strip()
    museum_dict[exhibit_id]['title'] = title

    desc = soup.find('div', class_="mde-column__section").get_text().strip()
    museum_dict[exhibit_id]['desc'] = desc

    date = soup.find('h2', class_="page-header__subheading--narrow").get_text().strip()
    museum_dict[exhibit_id]['date'] = date

def find_desc(soup):
    desc_string = ''
    if soup.find('div', class_ = 'inner-content'):
        desc_string = soup.find('div', class_ = 'inner-content').get_text()
    elif soup.find('meta', attrs = {'name': 'description'}):
        desc_string = soup.find('meta', attrs = {'name': 'description'})['content']
    elif soup.find('div', class_ = 'panel-pane pane-custom pane-3'):
        contains_desc = soup.find('div', class_ = 'panel-pane pane-custom pane-3').find_all('p')
     #   desc_string = ''
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
        start_end_date = start_date + ' - ' + end_date
    elif soup.find('div', id = 'dates'):
        start_end_date = soup.find('div', id = 'dates').find('h3').string
    elif soup.find('div', id = 'mainTitle'):
        start_end_date = soup.find('div', id = 'mainTitle').find('p').string
    
    return start_end_date

def build_deyoung(soup, museum_dict,exhibit_id):
    title = soup.find('title').get_text().strip()
    title = title[:-11]
    museum_dict[exhibit_id]['title'] = title

    museum_dict[exhibit_id]['desc'] = find_desc(soup)

    museum_dict[exhibit_id]['date'] = find_date(soup)

def build_legion(soup, museum_dict, exhibit_id):
    title = soup.find('title').get_text().strip()
    title = title[:-18]
    museum_dict[exhibit_id]['title'] = title

    museum_dict[exhibit_id]['desc'] = find_desc(soup)

    museum_dict[exhibit_id]['date'] = find_date(soup)

scrape_dict = { '001':{ 'name':     'Art Institute of Chicago',
                        'limiter':  "http://www.artic.edu/exhibition",
                        'page':     ["http://www.artic.edu/exhibitions"],
                        'restr':    ['http://www.artic.edu/exhibitions',
                                    'http://www.artic.edu/exhibitions/current',
                                    'http://www.artic.edu/exhibitions/upcoming',
                                    'http://www.artic.edu/exhibitions/past'],
                        'info':     build_artic },
                '002':{ 'limiter':  'https://mcachicago.org/Exhibitions',
                        'page':     ['https://mcachicago.org/Exhibitions'],
                        'restr':    ['https://mcachicago.org/Exhibitions/Series',
                                    'https://mcachicago.org/Exhibitions'],
                        'info':     build_mca   },
                '003':{  'limiter':  "http://www.newmuseum.org/exhibitions/view/",
                        'page':     ["http://www.newmuseum.org/exhibitions/current",
                                    "http://www.newmuseum.org/exhibitions/upcoming"],
                        'restr':    [],
                        'info':     build_new   },
                '004':{ 'limiter':  'http://www.moma.org/calendar/exhibitions/',
                        'page':     ['http://www.moma.org/calendar/exhibitions'],
                        'restr':    [],
                        'info':     build_moma  },
                '005':{ 'limiter':  'http://deyoung.famsf.org/exhibitions/',
                        'page':     ['http://deyoung.famsf.org/exhibitions/current',
                                    'http://deyoung.famsf.org/exhibitions/upcoming'],
                        'restr':    ['http://deyoung.famsf.org/exhibitions/current',
                                    'http://deyoung.famsf.org/exhibitions/deyoung/visiting/getting-de-young',
                                    'http://deyoung.famsf.org/exhibitions/upcoming',
                                    'http://deyoung.famsf.org/exhibitions/archive'],
                        'info':     build_deyoung   },
                '006':{ 'limiter':  'http://legionofhonor.famsf.org/exhibitions/',
                        'page':     ['http://legionofhonor.famsf.org/exhibitions/current',
                                    'http://legionofhonor.famsf.org/exhibitions/upcoming'],
                        'restr':    ['http://legionofhonor.famsf.org/exhibitions/current',
                                    'http://legionofhonor.famsf.org/exhibitions/upcoming',
                                    'http://legionofhonor.famsf.org/exhibitions/archive'],
                        'info':     build_legion    }   }

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
                restr = scrape_dict[museum_id]['restr']
                crawl(limiter, exhibit_urls, u, restr)

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

