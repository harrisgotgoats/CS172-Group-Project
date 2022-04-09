from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests
import re

class bjpenn_parse:

    def get_seed(self):
        url = 'https://www.bjpenn.com'
        r = requests.get("https://www.bjpenn.com/mma-news/ufc/jairzinho-rozenstruik-warns-marcin-tybura-of-his-power-ahead-of-ufc-273-as-soon-as-i-start-touching-people-they-have-big-problems/")
        soup = BeautifulSoup(r.text, 'html.parser')
        return soup


    def get_dirty_links(self, soup_obj):
        dirty_links = []
        unparsed_links = soup_obj.findAll('a')
        for link in unparsed_links:
            if link.has_attr('href') :
                dirty_links.append(link['href'])

        return dirty_links

    
    def __init__(self):
         bs = self.get_seed()
         links = self.get_dirty_links(bs)
         print(links)
        

def main():
   bjp = bjpenn_parse()


if __name__ == "__main__":
    main()