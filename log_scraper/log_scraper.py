from bs4 import BeautifulSoup
from path import path
import requests

def get_usernames():
    with open("uu/ladder_names.txt") as f:
        usernames = f.read().split("\n")
    return usernames

def get_log_usernames():
    names = path("./uu/logs")
    return names.listdir()


def get_user_replays(username):
    USERNAME_URL = "http://replay.pokemonshowdown.com/search/?output=html&user=%s" % username
    html = requests.get(USERNAME_URL).text
    soup = BeautifulSoup(html)
    links = soup.find_all('a')
    links = [link.get("href").encode("utf-8") for link in links if "uu" in link.get("href")]
    return links

def get_logs(link):
    html = requests.get("http://replay.pokemonshowdown.com" + link).text
    soup = BeautifulSoup(html)
    script = soup.find_all('script', {'class': 'log'})[0]
    log = script.text
    return log.encode('utf-8')

if __name__ == "__main__":
    usernames = get_usernames()
    for user in usernames:
        dir = path("./uu/logs") / user.decode("utf-8")
	if not dir.exists():
            dir.mkdir()
        links = get_user_replays(user)
	print user
        for link in links:
            directory = path("uu/logs/") / user
            log = get_logs(link)
            if not directory.exists():
                directory.makedirs()
            with open("uu/logs/%s/%s.log" % (user, link[1:]), 'w') as f:
                f.write(log)

