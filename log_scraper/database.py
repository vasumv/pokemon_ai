import sqlite3
from argparse import ArgumentParser

def parse_args():
    argparser = ArgumentParser()
    argparser.add_argument('db_path')

    return argparser.parse_args()

class ReplayDatabase(object):

    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)

        try:
            c = self.conn.cursor()
            c.execute("CREATE TABLE replay (_id INTEGER PRIMARY KEY AUTOINCREMENT, replay_id TEXT NOT NULL UNIQUE, battle_log TEXT)")
        except:
            pass

    def check_replay_exists(self, replay_id):
        c = self.conn.cursor()
        replay = c.execute("SELECT EXISTS(SELECT 1 FROM replay WHERE replay_id=? LIMIT 1)", [replay_id]).fetchone()
        return bool(replay[0])

    def get_replay(self, replay_id):
        c = self.conn.cursor()
        replay = c.execute("SELECT battle_log FROM replay WHERE replay_id=?", [replay_id]).fetchone()
        return replay[0]

    def add_replay(self, replay_id, battle_log):
        c = self.conn.cursor()
        c.execute("INSERT INTO replay (replay_id, battle_log) VALUES (?, ?)", [replay_id, battle_log])

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

if __name__ == "__main__":

    args = parse_args()
    r = ReplayDatabase(args.db_path)
