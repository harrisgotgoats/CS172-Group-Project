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
            if link.has_attr('href')  and validators.url(link['href']) and "https://www.bjpenn.com/mma-news/" in link['href']:
                dirty_links.append(link['href'])

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

    #Next step.
    def get_text_from_link(self, link):
        True

  
    def __init__(self):
        
         seed = self.get_seed("https://www.bjpenn.com/mma-news/")
         link_list = self.recurse_get_dirty_links(seed,[])
         filtered_link_list = self.filter_links(link_list)
         print(filtered_link_list)
       

def main():
   bjp = bjpenn_crawler()


if __name__ == "__main__":
    main()