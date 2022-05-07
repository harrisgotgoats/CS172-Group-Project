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
import csv
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

        with session.get(seed[1], timeout=10) as response:
            #get the soup object
            soup = bsf(response.text, 'html.parser')
            #Get all the links -- May need to implement better checks
            links = [[seed[0], l['href']] for l in soup.find_all('a') if (l.has_attr('href') and seed[0] in l['href'])]


            #data of the page - currently getting all the text from the page
            data = {
                'title': soup.title.text,
                'url': seed[1],
                'content': " ".join(p.text.strip() for p in soup.find_all("p"))
            }
            return links, data
    except requests.exceptions.Timeout:
        return None

    except:
        return None



'''
    The command line arguments are as follows:
    [1] = max_links (an integer specifying how many pages to scrape)
    [2] = max_threads (an integer specifying max number of threads to use for the ThreadPoolExecutor)
    [3] = filename (name of file containing seed links) | Leave empty to use the default
'''
if __name__ == "__main__":
    #List of starting urls - If new links added make sure to add the required checks and constraints
    default_url_pair = ["https://www.bjpenn.com/mma-news/","https://www.bjpenn.com/mma-news/ufc/dana-white-shuts-down-potential-francis-ngannou-tyson-fury-fight-fking-waste-of-time-energy-and-money/"]
    url_frontier = queue.Queue()
    explored_urls = set()

    if len(sys.argv) < 3:
        print("PLEASE SPECIFY ALL THE REQUIRED PARAMETERS")
        exit(1)
    elif not sys.argv[1].isnumeric() or not sys.argv[2].isnumeric():
        print("PLEASE ENTERY INTEGER VALUES FOR max_links and max_threads")
        exit(1)
    
    # Handles the use of an external file for adding url seed links.
    if len(sys.argv) == 4 and len(sys.argv[3]) > 0:
        if not os.path.exists(sys.argv[3]):
            print(f"ERROR: filename \"{sys.argv[3]}\" does not exist.")
            exit(1)
        with open(sys.argv[3], newline="") as seedfile:
            urlreader = csv.reader(seedfile)
            for common_full_pair in urlreader:
                url_frontier.put(common_full_pair)
    else:
        url_frontier.put(default_url_pair)

    # stores the data objects from each page
    data_found = []

    max_links = int(sys.argv[1])
    #Number of threads to use
    max_threads = int(sys.argv[2])

    executor = concurrent.futures.ThreadPoolExecutor(max_threads)

    # list of futures (threads that have not returned yet)
    futures = []
    start = time.time()
    while not url_frontier.empty():
        if len(data_found) >= max_links: break
        # If we have more than "batch_factor" urls scrape one more page. If there are more than "batch_factor" urls queue
        # queue a batch of "batch_factor" of pages to be crawled at the same time.
        while not url_frontier.empty():
            if len(data_found) >= max_links: break
            futures.append(executor.submit(scrape_link, url_frontier.get()))

        # Save the unique links returned by each thread and save their text data
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            if res == None:
                continue
            links, data = res
            data_found.append(data)

            if len(data_found) >= max_links: break

            for link in links:
                if link[1] in explored_urls:
                    continue

                url_frontier.put(link)
                explored_urls.add(link[1])

            print(f"Pages crawled: {len(data_found) + 1} / {max_links}", end="\r")
        # empties the futures list so that the next batch can be processed
        futures = []
    else:
        print("\nCould not find more URLs")
    
    print('\nCrawling Completed\nSaving data to ./Data.json...')
    with open('Data.json', 'w') as jfile:
        json.dump(data_found, jfile, indent=4)
    duration = datetime.timedelta(seconds=(time.time() - start))
    duration = str(duration).split('.')[0]
    duration = duration.split(':')
    print(f"Crawling completed in: {duration[0]} hrs: {duration[1]} mins : {duration[2]} secs")
    print("Data saved on Data.json")
    size = os.path.getsize("./Data.json") / 1000**2
    print(f"Total data collected: {round(size, 2)} MB")

    executor.shutdown(cancel_futures=True)
