import json
import requests
import validators
from bs4 import BeautifulSoup
from validators import ValidationFailure
from tail_call_optimized import *


#How the JSON will be represented.
class entry:
    link = ""
    html_text = ""

    def __init__(self,l,h) :
        self.link = l 
        self.html_text  = h


def bjpenn_crawler():
    
    

    def check_link(link):
        try:
            result = validators.url(link)
        except Exception as e:
            print(e)
            return False

        if isinstance(result, ValidationFailure):
             return False

        return True
    

    def get_seed(link):
   
        if check_link(link):
            r = requests.get(link)
            soup = BeautifulSoup(r.text, 'html.parser')
            return soup
        else:
            return None

    
    #gets all links on a page. grabs anythin with an <a href tag so some are garbage (like '#')

    def get_dirty_links(soup_obj):
        if not soup_obj:
            return []

        dirty_links = []
        unparsed_links = soup_obj.findAll('a')
        if not unparsed_links:
            return []

        for link in unparsed_links:
            if link.has_attr('href'):
                new_dirty_link = link['href']
                if "https://www.bjpenn.com/mma-news/" in new_dirty_link:

                    dirty_links.append(new_dirty_link)
        
        
        return dirty_links

   
    #recurse until terminate conditions are true, implemented with tail recursion (may need to modify server to expand stack limitation in python)
    @tail_call_optimized
    def recurse_get_dirty_links(soup_obj,link_dict,links_to_check):
        
        dirty_links = get_dirty_links(soup_obj)
        if dirty_links != []:
            for link in dirty_links:
                if link not in link_dict:
                    link_dict[link] = link
                    links_to_check.append(link)

        if(len(links_to_check) > 0):
            link = links_to_check[0]
            links_to_check.pop(0)
            recurse_get_dirty_links(get_seed(link), link_dict, links_to_check)
        else:
            return list(link_dict.values())
            
  
    def get_web_page(link):
        try:
            req = requests.get(link)
        except requests.exceptions.InvalidSchema as i:
            print(i)
            return ""

        return req.text
        
        
        
    def open_file(filename):
        file_reference = None
        
        try:
            file_reference.open(filename,'a')
        except IOError as e:
            print(e)
            exit(1)
            
        return file_reference
    
   
        
    def save_jsons(clean_link_list,filename):
        file = open_file(filename)

        for clean_link in clean_link_list:
            new_entry = entry(clean_link, get_web_page(clean_link))
            new_json = json.dumps(new_entry.__dict__)
            json.dump(new_json,file)
            



  
    seed_url = "https://www.bjpenn.com/mma-news/"
    filename = "jsons.data"
    
    seed = get_seed(seed_url)
    link_list = recurse_get_dirty_links(seed,{},[])
    print(len(link_list))
    save_jsons(link_list,filename)
       

def main():
   bjpenn_crawler()


if __name__ == "__main__":
    main()