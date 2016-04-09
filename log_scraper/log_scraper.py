from bs4 import BeautifulSoup
import requests
from argparse import ArgumentParser
from database import ReplayDatabase

LADDER_URL = "http://pokemonshowdown.com/ladder/ou"
USERNAME_URL = "http://replay.pokemonshowdown.com/search/?output=html&user={user}&format=&page={page}&output=html"
REPLAY_URL= "http://replay.pokemonshowdown.com/{replay_id}"

def parse_args():
    argparser = ArgumentParser()
    argparser.add_argument('db_path')
    argparser.add_argument('--start_index', default=0, type=int)
    argparser.add_argument('--end_index', default=499, type=int)
    argparser.add_argument('--max_page', default=100, type=int)

    return argparser.parse_args()

def get_usernames():
    text = requests.get(LADDER_URL).text
    soup = BeautifulSoup(text)
    return [t.text.encode('utf-8') for t in soup.find_all('a', {'class': 'subtle'})]

def page_done(database, replay_ids):
    first, last = replay_ids[0], replay_ids[-1]
    return database.check_replay_exists(first) and database.check_replay_exists(last)


def get_replay_ids(username, page, tier='ou'):
    final_links = []
    url = USERNAME_URL.format(
        user=username,
        page=page
    )
    html = requests.get(url).text
    soup = BeautifulSoup(html)
    links = soup.find_all('a')
    for link in links:
        if tier in link.get("href"):
            final_links.append(link.get("href").encode("utf-8")[1:])
    return final_links

def get_logs(replay_id):
    html = requests.get(REPLAY_URL.format(
        replay_id=replay_id)
    ).text
    soup = BeautifulSoup(html)
    script = soup.find_all('script', {'class': 'log'})[0]
    log = script.text
    return log

if __name__ == "__main__":
    args = parse_args()
    usernames = get_usernames()
    r = ReplayDatabase(args.db_path)
    for user in usernames[args.start_index:args.end_index]:
        print "User: %s" % user
        for i in range(1, args.max_page + 1):
            print "Page: %d" % i
            replay_ids = get_replay_ids(user, i)
            if page_done(r, replay_ids):
                print "Skipped page: %d" % i
                continue
            for replay_id in replay_ids:
                if not r.check_replay_exists(replay_id):
                    print "New replay ID: %s" % replay_id
                    r.add_replay(replay_id, get_logs(replay_id))
            r.commit()
