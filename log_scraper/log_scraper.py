from bs4 import BeautifulSoup
from path import Path
import requests

def get_usernames():
    with open("ou/ladder_names.txt") as f:
        usernames = f.read().split("\n")
    return usernames

def get_log_usernames():
    names = Path("./ou/logs")
    return names.listdir()


def get_user_replays(username):
    final_links = []
    for page in range(1, 5):
        USERNAME_URL = "http://replay.pokemonshowdown.com/search/?output=html&user=%s&format=&page=%d&output=html" % (username, page)
        html = requests.get(USERNAME_URL).text
        soup = BeautifulSoup(html)
        links = soup.find_all('a')
        for link in links:
            if "ou" in link.get("href"):
                final_links.append(link.get("href").encode("utf-8"))
    return final_links

def get_logs(link):
    html = requests.get("http://replay.pokemonshowdown.com" + link).text
    soup = BeautifulSoup(html)
    script = soup.find_all('script', {'class': 'log'})[0]
    log = script.text
    return log.encode('utf-8')

if __name__ == "__main__":
    usernames = get_usernames()
    log_names = []
    for user in usernames:
        if user == "metaang":
            continue
        user_path = Path("ou/logs") / user.decode("utf-8")
        if not user_path.exists():
            print 'making new directory'
            user_path.mkdir()
        logs = [x.basename() for x in user_path.listdir()]
        log_names += logs
        links = get_user_replays(user)
        print user
        for link in links:
            if (link[1:] + ".log") in log_names:
                continue
            print link
            directory = Path("ou/logs/") / user
            log = get_logs(link)
            if not directory.exists():
                directory.makedirs()
            with open("ou/logs/%s/%s.log" % (user, link[1:]), 'w') as f:
                f.write(log)
