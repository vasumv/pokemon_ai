from bs4 import BeautifulSoup
import requests

LADDER_URL = "http://pokemonshowdown.com/ladder/ou"
def get_ladder_html():
    return requests.get(LADDER_URL).text
def get_list(text):
    soup = BeautifulSoup(text)
    return soup.find_all('a', {'class': 'subtle'})
if __name__ == "__main__":
    text = get_ladder_html()
    names = get_list(text)
    with open('ladder_names.txt', 'w') as fp:
        for name in names:
            print >>fp, name.text.encode('utf-8')

