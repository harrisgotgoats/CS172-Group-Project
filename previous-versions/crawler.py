import json
import time
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from tqdm import tqdm
from bs4 import BeautifulSoup

def scrape(site):
    #Add delays
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    #Request the site
    response = requests.get(site)
    #Check for OK status code
    if response.status_code == 200:
        #Parse the site
        bs = BeautifulSoup(response.text, 'html.parser')
        #Get all 'a' tags
        links = bs.findAll('a')
        #Remove tags without 'href' attribute
        links_a = [l for l in links if l.has_attr('href')]
        #Store all links from 'href' in a list
        links_b = [l['href'] for l in links_a]
        #Only keep pages from the same site
        links_c = [l for l in links_b if 'https://www.bjpenn.com/mma-news/' in l]
        #Drop duplicates
        links_d = list(set(links_c))
        #Grab the 'body' tag and remove any 'style' and 'script' tags from it
        bs = bs.find('body')
        for data in bs(['style', 'script']):
            data.decompose()
        #Return list of links and texts from inside of 'body' tag
        return links_d, ' '.join(bs.stripped_strings)
    
    #Return empty list of links and empty text if there was an error
    return [], ""


if __name__ == "__main__":
    links = ['https://www.bjpenn.com/mma-news/']
    data = {}
    index = 0
    max_links = 30000

    #Loop until we are out of links or reach our max
    for i in tqdm (range(max_links), desc="Scraping..."):
        #If we run out of new links
        if(index >= len(links)):
            break;
        #Scrape current site
        new_links, html = scrape(links[index])
        #Append new links to the end of our list
        [links.append(l) for l in new_links if l not in links]
        #Save the current link and its html in the data
        data[links[index]] = html
        #Increment index
        index = index + 1
    
    #Save data into a file
    with open("data.json", "w") as outfile:
        json.dump(data, outfile)