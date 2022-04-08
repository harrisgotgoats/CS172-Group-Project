from bs4 import BeautifulSoup
import requests
import re

class bjpenn_parse:

    def parse(self):
        url = 'https://www.bjpenn.com'
        r = requests.get("https://www.bjpenn.com/mma-news/ufc/jairzinho-rozenstruik-warns-marcin-tybura-of-his-power-ahead-of-ufc-273-as-soon-as-i-start-touching-people-they-have-big-problems/")
        soup = BeautifulSoup(r.text, 'html.parser')
        return soup

    #need to fix regex for http urls.
    def parseLink(self, entry):
        url = re.findAll("http.*/",entry);
        print(url)

    def getRelativeLinks(self, soup):
            relative_links = soup.findAll('li')

            return relative_links

    ##dirty links are the entries inside the table. the links need to be parsed and stripped.
    def __init__(self):
         bs = self.parse()
         dirty_links = self.getRelativeLinks(bs)
        

def main():
   bjp = bjpenn_parse()
   print("test")


if __name__ == "__main__":
    main()