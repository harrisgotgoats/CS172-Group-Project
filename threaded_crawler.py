import json
from time import sleep
from unittest import result
from bs4 import BeautifulSoup
import requests
import validators
from validators import ValidationFailure
from tail_call_optimized import *
from concurrent.futures import ThreadPoolExecutor, as_completed


class Crawler:        
    
    def __init__(self, seed, scan_depth_limit):
        self.main_seed = seed
        self.main_url_set = set()
        self.scan_depth_limit = scan_depth_limit

    def check_link(self, link):
        try:
            result = validators.url(link)
        except Exception as e:
            return False

        if isinstance(result, ValidationFailure):
            return False

        return True
    

    def get_seed(self, link):
        if self.check_link(link):
            r = requests.get(link)
            soup = BeautifulSoup(r.text, 'html.parser')
            return soup
        else:
            return None

    
    #gets all links on a page. grabs anythin with an <a href tag so some are garbage (like '#')
    def get_dirty_links(self, soup_obj):
        if soup_obj == None:
            return set()

        dirty_links = set()
        unparsed_links = soup_obj.findAll('a')
        if unparsed_links == None:
            return set()

        for link in unparsed_links:
            if link.has_attr('href'):
                new_dirty_link = link['href']
                if "https://www.bjpenn.com/mma-news/" in new_dirty_link:

                    dirty_links.add(new_dirty_link) 
        
        return dirty_links

    def start(self, threads = 10):
        with ThreadPoolExecutor(threads) as executor:
            futures = []
            main_seed_soup = self.get_seed(self.main_seed)
            
            @tail_call_optimized
            def recursive_crawl(soup, url_acc, scan_depth):
                # get only the unique links in the page
                unique_links = self.get_dirty_links(soup).difference(url_acc)

                if(len(unique_links) != 0):
                    # union the two unique sets
                    url_acc |= unique_links
                
                if(scan_depth >= self.scan_depth_limit): 
                    return url_acc

                i = 0
                for link in unique_links:
                    i += 1
                    print(f"Crawling link [ SD : {scan_depth} | P : {i} ]")
                    futures.append(executor.submit(recursive_crawl, self.get_seed(link), url_acc, scan_depth + 1))

                #After making threads crawl the unique links return the unique links found on this page
                return url_acc

            futures.append(executor.submit(recursive_crawl, main_seed_soup, set(), 0))

            for future in as_completed(futures):
                self.main_url_set |= future.result()

        
            
    
    def getCurrentLinkSet(self):
        return self.main_url_set.copy()
        
        




if __name__ == "__main__":
    seed = "https://www.bjpenn.com/mma-news/ufc/jairzinho-rozenstruik-warns-marcin-tybura-of-his-power-ahead-of-ufc-273-as-soon-as-i-start-touching-people-they-have-big-problems/"
    depth_limit = 10 
    spider = Crawler(seed, depth_limit)
    spider.start(100)
    print(f"Total links found: {len(spider.getCurrentLinkSet())}")