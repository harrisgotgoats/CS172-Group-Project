import json
from re import L
from bs4 import BeautifulSoup
import requests
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError


class bjpenn_crawler:

    #How the JSON will be represented.
    class entry:
        link = ""
        text = ""

        def __init__(self,l,t) :
            self.link = l 
            self.link = t 

    def check_link(self, link):

        val = URLValidator()
        try:
            val(link)
        except(ValidationError):
            return False

        return True

    def get_seed(self,link):
   
        if self.check_link(link):
            r = requests.get(link)
            soup = BeautifulSoup(r.text, 'html.parser')
            return soup
        else:
            return None

    #gets all links on a page. grabs anythin with an <a href tag so some are garbage (like '#')
    def get_dirty_links(self, soup_obj):
        dirty_links = []
        unparsed_links = soup_obj.findAll('a')
        if unparsed_links == None:
            return []

        for link in unparsed_links:
            if link.has_attr('href'):
                new_dirty_link = link['href']
                if "https://www.bjpenn.com/mma-news/" in new_dirty_link:

                    dirty_links.append(new_dirty_link)

        
        return dirty_links

   
    #recurse until terminate conditions are true, implemented with tail recursion (may need to modify server to expand stack limitation in python)
    def recurse_get_dirty_links(self,soup_obj,link_list):
        def terminate_check():
            return len(link_list) > 200

        dirty_links = self.get_dirty_links(soup_obj)
        

        link_list.append(tuple(dirty_links))
        for link in dirty_links:
            if terminate_check():
                return link_list

            self.recurse_get_dirty_links(self.get_seed(link),link_list)

    #remove duplicates and possibly pre process further later on if needed
    def filter_links(self, dirty_link_list):
         no_duplicates = list(dict.fromkeys(tuple(dirty_link_list)))

         return no_duplicates

    #Parses the text on the page by searching between <p> tags. Returns one single string with all the text.
    def get_text_from_link(self, link):
        text = ""
        seed = self.get_seed(link)
        if seed == None:
            return ""
        
        p_tags = seed.findAll('p')
        try:
            for p_tag in p_tags:
                text += p_tag.getText()
        except(...):
            True

        return text
  
    #creates the objects that the I will then convert to JSON objects
    def get_entries(self, clean_link_list):
        entries = []
        for clean_link in clean_link_list:
            new_entry = self.entry(clean_link, self.get_text_from_link(clean_link))
            entries.append(new_entry)

        return entries

    #converts entries to jsons
    def get_jsons(self,entries):
        json_list = []
        for entry in entries:
            json_list.append(json.dumps(entry.__dict__))

        return json_list

    #filters out pages that have no text on them
    def filter_jsons(self,dirty_jsons):
        for key, value in dirty_jsons:
            if key == "text" and value == "":
                dirty_jsons.remove("")
        return dirty_jsons

    def print_jsons(self,json_list):
        for key, value in json_list:
            print(key,value)

    def __init__(self):
        
         seed = self.get_seed("https://www.bjpenn.com/mma-news/")
         link_list = self.recurse_get_dirty_links(seed,[])
         filtered_link_list = self.filter_links(link_list)
         entries = self.get_entries(filtered_link_list)
         json_objects = self.get_jsons(entries)
         filtered_jsons = self.filter_jsons(json_objects)
         self.print_jsons(filtered_jsons)
       

def main():
   bjp = bjpenn_crawler()


if __name__ == "__main__":
    main()