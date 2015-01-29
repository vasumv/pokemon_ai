from bs4 import BeautifulSoup
from path import path
import requests

def get_usernames():
    with open("ladder_names.txt") as f:
        usernames = f.read().split("\n")
    return usernames

def get_log_usernames():
    names = path("./logs")
    return names.listdir()


def get_user_replays(username):
    USERNAME_URL = "http://replay.pokemonshowdown.com/search/?output=html&user=%s" % username
    html = requests.get(USERNAME_URL).text
    soup = BeautifulSoup(html)
    links = soup.find_all('a')
    links = [link.get("href").encode("utf-8") for link in links if "ou" in link.get("href")]
    return links

def get_logs(link):
    html = requests.get("http://replay.pokemonshowdown.com" + link).text
    soup = BeautifulSoup(html)
    script = soup.find_all('script', {'class': 'log'})[0]
    log = script.text
    return log.encode('utf-8')

if __name__ == "__main__":
    usernames = get_usernames()
    user = "WECAMEASROMANS"
    for user in usernames:
        dir = path("./logs") / user.decode("utf-8")
        if not dir.exists():
            continue
        already_logs = dir.files()
        print user
        links = get_user_replays(user)
        for link in links:
            if (dir + link + ".log") in already_logs:
                continue
            directory = path("logs/") / user
            log = get_logs(link)
            if not directory.exists():
                directory.makedirs()
            with open("logs/%s/%s.log" % (user, link[1:]), 'w') as f:
                f.write(log)
            print "writing new log"

