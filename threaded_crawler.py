import requests
import json
import concurrent.futures
import threading
from bs4 import BeautifulSoup as bsf
import time
import os

thread_local = threading.local()

def get_session():
    if not hasattr(thread_local, 'session'):
        thread_local.session = requests.Session()
    return thread_local.session


def scrape_link(seed): # returns the links and data from this seed_link
    session = get_session()
    with session.get(seed) as response:
        soup = bsf(response.text, 'html.parser')
        links = [l['href'] for l in soup.find_all('a') if (l.has_attr('href') and "https://www.bjpenn.com/mma-news" in l['href'])]
        data = {
            'title': soup.title.text,
            'url': seed,
            'content': ''.join([p.text.strip() for p in soup.find_all('p')])
        }
        return links, data

if __name__ == "__main__":
    urls = [
        "https://www.bjpenn.com/mma-news/ufc/jairzinho-rozenstruik-warns-marcin-tybura-of-his-power-ahead-of-ufc-273-as-soon-as-i-start-touching-people-they-have-big-problems/",
    ]
    data_found = []
    futures = []
    max_links = 1000
    batch_factor = 10
    with concurrent.futures.ThreadPoolExecutor() as executor:
        start = time.time()
        for i in range(max_links):
            if i >= len(urls):
                print("Could not find more links")
                break
            if(len(data_found) >= max_links): break
            if(len(urls) - i > batch_factor):
                for j in range(batch_factor):
                    futures.append(executor.submit(scrape_link, urls[i]))
                    i += 1
            else: 
                futures.append(executor.submit(scrape_link, urls[i]))

            for future in concurrent.futures.as_completed(futures):
                links, data = future.result()
                data_found.append(data)
                for l in links:
                    if l not in urls:
                        if(len(data_found) >= max_links): break
                        urls.append(l)
                if(len(data_found) >= max_links): break
                print(f"Pages crawled: {len(data_found)}", end="\r")
            futures = []
        
            
        print('\n')
        with open('Data.json', 'w') as jfile:
            json.dump(data_found, jfile, indent=4)
        print(f"Crawling completed in: {round(time.time() - start, 3)} seconds")
        size = os.path.getsize("./Data.json") / 1024**2
        print(f"Total data collected: {round(size, 2)} MB")