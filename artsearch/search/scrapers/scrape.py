import requests
import bs4
import util
import re

def crawl(limiter, exhibit_urls, u, restr):
    '''
    crawls u and adds qualifying links to exhibit_urls 
    inputs:
        limiter: url stem that we want the exhibit links to start with
        exhibit_urls: list that we are adding links to
        u: the page we are crawling
        restr: restricted pages that we don't want to add to exhibit_urls
    outputs:
        modifies exhibit_urls
    '''
    if  (limiter in u) and (u not in exhibit_urls) and \
        (u not in restr) and (restricted_string not in u):
        exhibit_urls += [u]

restricted_string = "http://www.artic.edu/exhibitions?qt-media_feed"

def build_artic(soup, museum_dict, exhibit_id):
    '''
    pulls information from html soup
    inputs:
        soup: soup for exhibit url we are on 
        museum_dict: dictionary
        exhibit_id: id assigned to this exhibit 
    outpus:
        modifies museum_dict
    '''
    title = soup.find('title').get_text().strip()
    title = title[:-31]
    museum_dict[exhibit_id]['title'] = title 

    desc = soup.find('div',class_='field-item even', 
           property="content:encoded").get_text().strip()
    museum_dict[exhibit_id]['desc'] = desc

    date = soup.find('div',class_ = "field-item even").get_text().strip()
    museum_dict[exhibit_id]['date'] = date

def build_mca(soup, museum_dict, exhibit_id):
    '''
    pulls information from html soup
    inputs:
        soup: soup for exhibit url we are on 
        museum_dict: dictionary
        exhibit_id: id assigned to this exhibit 
    outpus:
        modifies museum_dict
    '''
    title = soup.find('title').get_text().strip()
    title = title[6:]
    museum_dict[exhibit_id]['title'] = title 

    desc = soup.find('div', class_="bg_white").get_text().strip()
    museum_dict[exhibit_id]['desc'] = desc
    
    date = soup.find('p',class_="dates").get_text().strip()
    museum_dict[exhibit_id]['date'] = date

def build_new(soup, museum_dict, exhibit_id):
    '''
    pulls information from html soup
    inputs:
        soup: soup for exhibit url we are on 
        museum_dict: dictionary
        exhibit_id: id assigned to this exhibit 
    outpus:
        modifies museum_dict
    '''
    title = soup.find('h3', style='color: #fff;').get_text().strip()
    museum_dict[exhibit_id]['title'] = title

    desc = soup.find('div', class_="body").get_text().strip()
    museum_dict[exhibit_id]['desc'] = desc

    date = soup.find('p', class_="date-range").get_text().strip()
    museum_dict[exhibit_id]['date'] = date
                   
def build_moma(soup, museum_dict, exhibit_id):
    '''
    pulls information from html soup
    inputs:
        soup: soup for exhibit url we are on 
        museum_dict: dictionary
        exhibit_id: id assigned to this exhibit 
    outpus:
        modifies museum_dict
    '''
    title = soup.find('h1', class_="page-header__title").get_text().strip()
    museum_dict[exhibit_id]['title'] = title

    desc = soup.find('div', class_="mde-column__section").get_text().strip()
    museum_dict[exhibit_id]['desc'] = desc

    date = soup.find('h2', 
           class_="page-header__subheading--narrow").get_text().strip()
    museum_dict[exhibit_id]['date'] = date

# ======================
# FINDERS

def find_desc_legion(soup):
    '''
    finds description in the soup for Legion of Honor's exhibit pages
    inputs:
        soup
    outputs:
        desc_string: exhibit description as string
    '''
    desc_string = ''
    if soup.find('div', class_= 'panel-pane pane-custom pane-4').find_all('p'):
        contains_desc = soup.find('div', 
                        class_= 'panel-pane pane-custom pane-4').find_all('p')
        for d in contains_desc:
            if d.get_text():
                desc_string += d.get_text()
            else:
                break
    elif soup.find_all('div', class_ = 'field-item even'):
        contains_desc = soup.find_all('div', class_ = 'field-item even')
        desc_string = contains_desc[4].get_text()
    
    return desc_string

def find_desc_deyoung(soup):
    '''
    finds description in the soup for de Young's exhibit pages
    inputs:
        soup
    outputs:
        desc_string: exhibit description as string
    '''
    desc_string = ''
    if soup.find('div', class_="inner-content"):
        desc_string = soup.find('div', class_='inner-content').get_text()
    elif soup.find('div', class_ = 'panel-pane pane-custom pane-3'):
        contains_desc = soup.find('div', 
                        class_ = 'panel-pane pane-custom pane-3').find_all('p')
        for d in contains_desc:
            if d.get_text():
                desc_string += d.get_text()
            else:
                break
    elif soup.find_all('div',class_='field-item even'):
        contains_desc=soup.find_all('div', class_='field-item even')
        desc_string = contains_desc[4].get_text()
    return desc_string

def find_date(soup):
    '''
    finds date in the soup for the exhibit page
    inputs:
        soup
    outputs:
        date: exhibit date as string
    '''
    if soup.find('span', class_ = 'date-display-start'):
        start_date = soup.find('span', class_ = 'date-display-start').string
        end_date = soup.find('span', class_ = 'date-display-end').string
        date = start_date + ' - ' + end_date
    elif soup.find('div', id = 'dates'):
        date = soup.find('div', id = 'dates').find('h3').string

    elif soup.find('div', id = 'mainTitle'):
        date = soup.find('div', id = 'mainTitle').find('p').string
   
    return date

# ======================

def build_deyoung(soup, museum_dict,exhibit_id):
    '''
    pulls information from html soup
    inputs:
        soup: soup for exhibit url we are on 
        museum_dict: dictionary
        exhibit_id: id assigned to this exhibit 
    outputs:
        modifies museum_dict
    '''
    title = soup.find('title').get_text().strip()
    title = title[:-11]
    museum_dict[exhibit_id]['title'] = title

    museum_dict[exhibit_id]['desc'] = find_desc_deyoung(soup)

    museum_dict[exhibit_id]['date'] = find_date(soup)


def build_legion(soup, museum_dict, exhibit_id):
    '''
    pulls information from html soup
    inputs:
        soup: soup for exhibit url we are on 
        museum_dict: dictionary
        exhibit_id: id assigned to this exhibit 
    outputs:
        modifies museum_dict
    '''
    title = soup.find('title').get_text().strip()
    title = title[:-18]
    museum_dict[exhibit_id]['title'] = title

    museum_dict[exhibit_id]['desc'] = find_desc_legion(soup)

    museum_dict[exhibit_id]['date'] = find_date(soup)

def build_whitney(soup, museum_dict, exhibit_id):
    '''
    pulls information from html soup
    inputs:
        soup: soup for exhibit url we are on
        museum_dict: dictionary
        exhibit_id: id assigned to this exhibit 
    outputs:
        modifies museum_dict
    '''

    title = soup.find_all('title')
    title = title[0].get_text().strip()
    title = title[:-33]
    if title == "Human Interest:Portraits from the Whitney's Collection Apr 27, 2016-Feb 12, 2017":
        date = title[55:]
        title = title[:-26]
    museum_dict[exhibit_id]['title'] = title

    desc = soup.find_all('div',class_="text-module-text text-larger")
    desc = desc[0].get_text().strip()
    museum_dict[exhibit_id]['desc'] = desc

    if title != "Human Interest:Portraits from the Whitney's Collection":
        date = soup.find_all('div',class_="wrapper")
        date = date[0].find('h2').get_text().strip()
    museum_dict[exhibit_id]['date'] = date

scrape_dict = { '001':{ 'name':     'Art Institute of Chicago',
                        'limiter':  "http://www.artic.edu/exhibition",
                        'page':     ["http://www.artic.edu/exhibitions"],
                        'restr':    ['http://www.artic.edu/exhibitions',
                                    'http://www.artic.edu/exhibitions/current',
                                    'http://www.artic.edu/exhibitions/upcoming',
                                    'http://www.artic.edu/exhibitions/past'],
                        'info':     build_artic }, 
                '002':{ 'name':     'Museum of Contemporary Art',
                        'limiter':  'https://mcachicago.org/Exhibitions',
                        'page':     ['https://mcachicago.org/Exhibitions'],
                        'restr':    ['https://mcachicago.org/Exhibitions/Series',
                                    'https://mcachicago.org/Exhibitions', 
                                    'https://mcachicago.org/Exhibitions/Artists-In-Residence'],
                        'info':     build_mca   },
                '003':{ 'name':     'New Museum',
                        'limiter':  "http://www.newmuseum.org/exhibitions/view/",
                        'page':     ["http://www.newmuseum.org/exhibitions/current",
                                    "http://www.newmuseum.org/exhibitions/upcoming"],
                        'restr':    [],
                        'info':     build_new   },
                '004':{ 'name':     'Museum of Modern Art',
                        'limiter':  'http://www.moma.org/calendar/exhibitions/',
                        'page':     ['http://www.moma.org/calendar/exhibitions'],
                        'restr':    [],
                        'info':     build_moma  },
                '005':{ 'name':     'de Young Museum',
                        'limiter':  'http://deyoung.famsf.org/exhibitions/',
                        'page':     ['http://deyoung.famsf.org/exhibitions/current',
                                    'http://deyoung.famsf.org/exhibitions/upcoming'],
                        'restr':    ['http://deyoung.famsf.org/exhibitions/current',
                                    'http://deyoung.famsf.org/exhibitions/deyoung/visiting/getting-de-young',
                                    'http://deyoung.famsf.org/exhibitions/upcoming',
                                    'http://deyoung.famsf.org/exhibitions/archive'],
                        'info':     build_deyoung   },
                '006':{ 'name':     'Legion of Honor',
                        'limiter':  'http://legionofhonor.famsf.org/exhibitions/',
                        'page':     ['http://legionofhonor.famsf.org/exhibitions/current',
                                    'http://legionofhonor.famsf.org/exhibitions/upcoming'],
                        'restr':    ['http://legionofhonor.famsf.org/exhibitions/current',
                                    'http://legionofhonor.famsf.org/exhibitions/upcoming',
                                    'http://legionofhonor.famsf.org/exhibitions/archive'],
                        'info':     build_legion    },
                '007':{ 'name':     'Whitney Museum of American Art',
                        'limiter':  "http://whitney.org/Exhibitions",
                        'page':     ["http://whitney.org/Exhibitions",
                                    "http://whitney.org/Exhibitions/Upcoming"],
                        'restr':    ["http://whitney.org/Exhibitions",
                                    "http://whitney.org/Exhibitions/Upcoming",
                                    "http://whitney.org/Exhibitions/Past",
                                    "http://whitney.org/Exhibitions/Touring",
                                    "http://whitney.org/Exhibitions/Film",
                                    "http://whitney.org/Exhibitions/Performance",
                                    "http://whitney.org/Exhibitions/Artport"],
                        'info':     build_whitney}}   

def scrape():
    '''
    performs entire scraping function
    outputs:
        index: dictionary of museum/exhibit information 
    '''
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
            print(link)
            try:
                index[museum_id][exhibit_id] = {}
                scrape_dict[museum_id]['info'](soup, index[museum_id], exhibit_id)
                index[museum_id][exhibit_id]['url'] = link
                exhibit_id = '00' + str(int(exhibit_id) + 1)
            except:
                print('\t^^ Scraper Failed')

        
        with open('../csvs/musid_name.csv','w') as f:
            line = 'mus_id|name' + '\n'
            f.write(line)
            for mus_id in scrape_dict:
                line = '{}|{}\n'.format(str(mus_id), \
                    scrape_dict[mus_id]['name'])
                f.write(line) 

    return index


