from bs4 import BeautifulSoup

def parse():
    url = 'https://www.bjpenn.com'
    r = requests.get("https://www.bjpenn.com/mma-news/ufc/jairzinho-rozenstruik-warns-marcin-tybura-of-his-power-ahead-of-ufc-273-as-soon-as-i-start-touching-people-they-have-big-problems/")
    soup - BeautifulSoup(r.text, 'html.parser')

    