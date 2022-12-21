import re
import requests
import bs4
import json
from requests import Session
# 22 lines

cache = {}
def hashable_cache(f):
    def inner(url, session):
        if url not in cache:
            cache[url] = f(url, session)
        return cache[url]
    return inner

@hashable_cache
def get_first_paragraph(url, session: Session):
    req = session.get(url)
    soup = bs4.BeautifulSoup(req.text, "html.parser")
    for paragraph in soup.find_all('p'):
        if paragraph.find_all('b'):                    
            p = paragraph.text
            pattern = "\(.*/.*/[^\)]*\)"
            #pattern = r"\((.+?)\)"
            p = re.sub(pattern,'',p)

            pattern = "(\n|\xa0)" #delete html part (replace by a space), may be others??? => due to russian
            p = re.sub(pattern, ' ', p)
            
            pattern = "\[..?\]"    #delete references (max 2 letters/numers)
            p = re.sub(pattern, ' ', p)
            break
        if paragraph.find_all('b'):
            print(paragraph.text)
            
    return p
        
            
    return first_paragraph

def get_cookies():
    root_url = "https://country-leaders.onrender.com"
    cookie_url = "/cookie"
    req = requests.get(root_url + cookie_url)
    cookies = req.cookies
    return cookies

def get_leaders():
    root_url = "https://country-leaders.onrender.com"
    
    cookies = get_cookies()
    
    country_url = "/countries"
    countries = requests.get(root_url + country_url, cookies=cookies)
    all_countries = countries.json()
    
    leaders_url = "/leaders"
    all_leaders = {}
    with Session() as session:
        for country in all_countries:
            
            req = requests.get(root_url + leaders_url, cookies = cookies, params = {"country": country})
            if req.status_code == 403:
                cookies = get_cookies()
                req = requests.get(root_url + leaders_url, cookies = cookies, params = {"country": country})
                
            if req.status_code == 200:
                req_json = req.json()
                for leader in req_json:
                    if leader['first_name'] +' '+ leader['last_name'] in all_leaders:   #!!!! some have the same names
                        all_leaders[leader['first_name'] +' '+ leader['last_name']] += get_first_paragraph(leader['wikipedia_url'], session) 
                    else:
                        all_leaders[leader['first_name'] +' '+ leader['last_name']] = get_first_paragraph(leader['wikipedia_url'], session)
            
        
    return all_leaders

def save(leaders_per_country):
    file = open("./leaders.json", "w")
    json.dump(leaders_per_country, file)
    file.close()
    
    
leaders_per_country = get_leaders()
save(leaders_per_country)