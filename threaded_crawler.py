import requests
import json
import threading
import concurrent.futures
from bs4 import BeautifulSoup as bsf
import time
import datetime
import os
import sys
import queue
from requests.adapters import HTTPAdapter, Retry


thread_local = threading.local()


#Starts a request session local to each thread
def get_session():
    if not hasattr(thread_local, 'session'):
        thread_local.session = requests.Session()
    return thread_local.session


def scrape_link(seed): # returns the links and data from this seed_link
    #gets the local session 
    try:
        session = get_session()

        retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500,502,503,504])

        session.mount('http://', HTTPAdapter(max_retries=retries))

        with session.get(seed, timeout=5) as response:
            #get the soup object
            soup = bsf(response.text, 'html.parser')
            #Get all the links -- May need to implement better checks
            links = [l['href'] for l in soup.find_all('a') if (l.has_attr('href') and "https://www.bjpenn.com/mma-news" in l['href'])]
            

            title = soup.find("h1", attrs={"class" : "entry-title"})
            if title:
                title = title.text
            else:
                title = soup.title.text
            content = soup.find("div", attrs={"class" : "td-post-content tagdiv-type"})
            if content:
                content = " ".join(p.text.strip() for p in content.find_all("p"))
            else:
                content = " ".join(p.text.strip() for p in soup.find_all("p"))

            #data of the page - currently getting all the text from the page
            data = {
                'title': title,
                'url': seed,
                'content': content
            }
            return links, data
    except requests.exceptions.Timeout:
        return None

    except:
        return None



'''
    The command line arguments are as follows:
    [1] = max_links (an integer specifying how many pages to scrape)
    [3] = max_threads (an integer specifying max number of threads to use for the ThreadPoolExecutor < batch_factor for better perfomance)
    [4] = filename (name of file containing seed links) | Leave empty to use the default
'''
if __name__ == "__main__":
    #List of starting urls - If new links added make sure to add the required checks and constraints
    default_url = "https://www.bjpenn.com/mma-news/ufc/dana-white-shuts-down-potential-francis-ngannou-tyson-fury-fight-fking-waste-of-time-energy-and-money/"
    url_frontier = queue.Queue()
    explored_urls = set()
    # Handles the use of an external file for adding url seed links.
    if len(sys.argv) == 4 and len(sys.argv[3]) > 0:
        if not os.path.exists(sys.argv[3]):
            print(f"ERROR: filename \"{sys.argv[3]}\" does not exist.")
            exit(1)
        with open(sys.argv[3], "r") as f:
            for url in f:
                url_frontier.put(url)
    else:
        url_frontier.append(default_url)

    # stores the data objects from each page
    data_found = []

    max_links = int(sys.argv[1])
    #Number of threads to use
    max_threads = int(sys.argv[2])

    with concurrent.futures.ThreadPoolExecutor(max_threads) as executor:
        # list of futures (threads that have not returned yet)
        futures = []
        start = time.time()
        while not url_frontier.empty() and len(data_found) < max_links:
            # If we have more than "batch_factor" urls scrape one more page. If there are more than "batch_factor" urls queue
            # queue a batch of "batch_factor" of pages to be crawled at the same time.
            while(url_frontier.qsize() > 0):
                if len(futures) + len(data_found) >= max_links: break
                futures.append(executor.submit(scrape_link, url_frontier.get()))

            # Save the unique links returned by each thread and save their text data
            for future in concurrent.futures.as_completed(futures):
                res = future.result()
                if res == None:
                    continue
                links, data = res
                data_found.append(data)
                
                # Don't add more links if we already have enough in the queue.
                if url_frontier.qsize() + len(data_found) < max_links:
                    unique_links = set(links) - explored_urls

                    if len(data_found) >= max_links: break

                    for link in unique_links:
                        url_frontier.put(link)
                        explored_urls.add(link)

                print(f"Queue size: {url_frontier.qsize()} | Pages crawled: {len(data_found)} / {max_links}", end="\r")
            # empties the futures list so that the next batch can be processed
            futures = []

        
            
        print('\n')
        with open('Data.json', 'w') as jfile:
            json.dump(data_found, jfile, indent=4)
        duration = datetime.timedelta(seconds=(time.time() - start))
        duration = str(duration).split('.')[0]
        duration = duration.split(':')
        print(f"Crawling completed in: {duration[0]} hrs: {duration[1]} mins : {duration[2]} secs")
        print("Data saved on Data.json")
        size = os.path.getsize("./Data.json") / 1000**2
        print(f"Total data collected: {round(size, 2)} MB")
