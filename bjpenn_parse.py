from bs4 import BeautifulSoup
import requests
import validators 

class bjpenn_crawler:

    def get_seed(self,link):
        r = requests.get(link)
        soup = BeautifulSoup(r.text, 'html.parser')
        return soup

    #gets all links on a page. grabs anythin with an <a href tag so some are garbage (like '#')
    def get_dirty_links(self, soup_obj):
        dirty_links = []
        unparsed_links = soup_obj.findAll('a')
        for link in unparsed_links:
            if link.has_attr('href')  and validators.url(link['href']) :
                dirty_links.append(link['href'])

        return dirty_links

    #need to fix infinite loop, i think the condition applies to each function call and it doesnt check the 'super' link_list
    def recurse_get_dirty_links(self,soup_obj):
        
        link_list = []
        dirty_links = self.get_dirty_links(soup_obj)
        if len(dirty_links) == 0 or len(link_list) > 200:
            return list

        link_list.append(dirty_links)
        for link in dirty_links:
            link_list.append(self.recurse_get_dirty_links(self.get_seed(link)))


        return link_list

    def __init__(self):
        

         seed = self.get_seed("https://www.bjpenn.com/mma-news/")
         links = self.recurse_get_dirty_links(seed)
         print(links)
        

def main():
   bjp = bjpenn_crawler()


if __name__ == "__main__":
    main()