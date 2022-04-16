import requests
import json
import concurrent.futures
import threading
from bs4 import BeautifulSoup as bsf
import time
import datetime
import os
import math


thread_local = threading.local()


#Starts a request session local to each thread
def get_session():
    if not hasattr(thread_local, 'session'):
        thread_local.session = requests.Session()
    return thread_local.session


def scrape_link(seed): # returns the links and data from this seed_link
    #gets the local session 
    session = get_session()
    with session.get(seed) as response:
        #get the soup objec
        try:
            soup = bsf(response.text, 'html.parser')
            #Get all the links -- May need to implement better checks
            links = [l['href'] for l in soup.find_all('a') if (l.has_attr('href') and "https://www.bjpenn.com/mma-news" in l['href'])]
            #data of the page - currently getting all the text from the page
            data = {
                'title': soup.title.text,
                'url': seed,
                'content': soup.text.strip()
             }
        except:
            return None,None
        return links, data

if __name__ == "__main__":
    #List of starting urls - If new links added make sure to add the required checks and constraints
    urls = [
        "https://www.bjpenn.com/mma-news/ufc/jairzinho-rozenstruik-warns-marcin-tybura-of-his-power-ahead-of-ufc-273-as-soon-as-i-start-touching-people-they-have-big-problems/",
    ]
    # stores the data objects from each page
    data_found = []

    max_links = 250000
    #How many pages are processed per iteration
    batch_factor = 80
    #Number of threads to use
    max_threads = math.floor(batch_factor / 2)
    with concurrent.futures.ThreadPoolExecutor(max_threads) as executor:
        # list of futures (threads that have not returned yet)
        futures = []
        start = time.time()
        for i in range(max_links):
            if i >= len(urls):
                print("Could not find more links")
                break
            #Crawled the number of pages requested
            if(len(data_found) >= max_links): break

            # If we have more than "batch_factor" urls scrape one more page. If there are more than "batch_factor" urls queue
            # queue a batch of "batch_factor" of pages to be crawled at the same time.
            if(len(urls) - i > batch_factor):
                for j in range(batch_factor):
                    futures.append(executor.submit(scrape_link, urls[i]))
                    i += 1
            else: 
                futures.append(executor.submit(scrape_link, urls[i]))

            # Save the unique links returned by each thread and save their text data
            for future in concurrent.futures.as_completed(futures):
                links, data = future.result()
                if not links:
                    continue
                data_found.append(data)
                for l in links:
                    if l not in urls:
                        if(len(data_found) >= max_links): break
                        urls.append(l)
                if(len(data_found) >= max_links): break
                print(f"Pages crawled: {len(data_found)} / {max_links}", end="\r")
            # empties the futures list so that the next batch can be processed
            futures = []
        
            
        print('\n')
        with open('Data.json', 'w') as jfile:
            json.dump(data_found, jfile, indent=4)
        duration = time.time() - start
        print(f"Crawling completed in: {datetime.timedelta(seconds=duration)} seconds")
        size = os.path.getsize("./Data.json") / 1000**2
        print(f"Total data collected: {round(size, 2)} MB")
