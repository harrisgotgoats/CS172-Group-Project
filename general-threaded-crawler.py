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
import re
import math


thread_local = threading.local()

# Starts a request session local to each thread
def get_session():
    if not hasattr(thread_local, 'session'):
        thread_local.session = requests.Session()
    return thread_local.session

# Returns the links found and data from this seed_link
def scrape_url(url):
    # Gets the local session
    try:
        session = get_session()
        retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500,502,503,504])
        session.mount('http://', HTTPAdapter(max_retries=retries))
        
        with session.get(url, timeout=10) as response:
            # Parse url using BeautifulSoup
            soup = bsf(response.text, 'html.parser')
            
            # Get all the links from url that has href attribute
            links = [l['href'] for l in soup.find_all('a') if l.has_attr('href')]
            
            # Remove blacklisted links, links that doesn't start with http or /
            # And add domain to relative links
            new_links = []
            for l in links:
                # Check for blacklisted links
                if not any(bl in l for bl in blacklist):
                    # If link starts with /, add scheme and domain to the front and add to list
                    if l.startswith("/"):
                        domain = get_domain(url)
                        if domain:
                            new_links.append(domain + l)
                    # If link starts with http, add to list
                    elif l.startswith("http"):
                        new_links.append(l)
            
            # Only get the body of the page and remove any styles and scripts
            content = soup.find('body')
            # Return nothing if content is empty ( probably from RSS )
            if not content:
                return None
            for data in content(['style', 'script']):
                data.decompose()
            
            # Store data of the page - currently getting all the text from the page
            data = {
                'title': soup.title.text,
                'url': url,
                'content': content.text.strip(),
            }
            return new_links, data
        
    except requests.exceptions.Timeout:
        return None
    
    except Exception as e:
        print("\n")
        print("Exception Occurred for", url)
        print(e)
        return None

# Parse the url and return scheme, subdomain, and domain
def get_domain(url):
    regex_string = "^(https?:\/\/[A-Za-z_0-9.-]+).*"
    match = re.search(regex_string, url)
    if(match):
        return match.group(1).lower()
    return ""

# Add either the list of urls or a single url to the queue and update explored_urls set
def add_to_queue(url):
    if type(url) == str:
        url_frontier.put(url)
        explored_urls.add(url)
    else:
        for u in url:
            url_frontier.put(u)
            explored_urls.add(u)


'''
    The command line arguments are as follows:
    [1] = max_urls (an integer specifying how many pages to scrape)
    [2] = max_threads (an integer specifying max number of threads to use for the ThreadPoolExecutor)
    [3] = url_count_threshold (an integer specifying an amount of minimum unique links crawled in order for the whole site to be crawled 
    [4] = seed links | Leave empty to use the default
'''
if __name__ == "__main__":
    # List of starting urls
    default_urls = ["https://www.bjpenn.com/mma-news/"]
    url_frontier = queue.Queue()
    explored_urls = set()

    if len(sys.argv) < 4:
        print("PLEASE SPECIFY ALL THE REQUIRED PARAMETERS")
        exit(1)
    elif not sys.argv[1].isnumeric() or not sys.argv[2].isnumeric() or not sys.argv[3].isnumeric():
        print("PLEASE ENTERY INTEGER VALUES FOR max_links, max_threads, and url_count_threshold")
        exit(1)
    
    # Handles the use of an external file for adding url seed links.
    if len(sys.argv) == 5 and len(sys.argv[4]) > 0:
        if not os.path.exists(sys.argv[4]):
            print(f"ERROR: filename \"{sys.argv[4]}\" does not exist.")
            exit(1)
        with open(sys.argv[4], newline="") as seedfile:
            urlreader = csv.reader(seedfile)
            add_to_queue(urlreader)
    else:
        add_to_queue(default_urls)

    # Stores the data objects from each page
    data_found = []
    
    # Blacklist social media and common sites
    blacklist = ['twitter', 'https://t.co/', 'instagram', 'youtube', 'https://youtu.be/', 'google', 'facebook', 'pinterest']
    
    # Keep track of url counts for each domain found ## {domain: [urls]}
    url_count = {}

    # Store user arguments
    max_links = int(sys.argv[1])
    max_threads = int(sys.argv[2])
    url_count_threshold = int(sys.argv[3])

    batch_factor = 0 # Dynamically determines the number of links processed per cycle

    # Create a set for domains we are already scraping
    already_scraping = set()
    for u in list(url_frontier.queue):
        domain = get_domain(u)
        if(domain):
            already_scraping.add(domain)
    
    executor = concurrent.futures.ThreadPoolExecutor(max_threads)
    
    futures = []
    start = time.time()
    while not url_frontier.empty():
        if len(data_found) >= max_links:
            break

        batch_factor = math.floor(url_frontier.qsize() / 
                                                        (math.log(url_frontier.qsize(), 2) + 1))

        for i in range(batch_factor):
            if len(data_found) >= max_links:
                break
            futures.append(executor.submit(scrape_url, url_frontier.get()))

        # Save the unique links returned by each thread and save their text data
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            if res == None:
                continue
            links, data = res
            data_found.append(data)

            if len(data_found) >= max_links:
                break

            for l in links:
                if l not in explored_urls:
                    # Add / to all urls to keep it consistent
                    if l[-1] != '/':
                        l += '/'

                    domain = get_domain(l)
                    if domain:
                        if domain in already_scraping:
                            add_to_queue(l)
                        else:
                            if domain not in url_count:
                                url_count[domain] = set([l])
                            else:
                                count = len(url_count[domain])
                                if count < url_count_threshold:
                                    url_count[domain].add(l)
                                elif (count == url_count_threshold) and (l not in url_count[domain]):
                                    url_count[domain].add(l)
                                    add_to_queue(url_count[domain])
                                    already_scraping.add(domain)
                                    del url_count[domain]

            print(f"Pages crawled: {len(data_found) + 1} / {max_links}", end="\r")
        
        # Empties the futures list so that the next batch can be processed
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

    executor.shutdown(wait=False)