from smogon import SmogonMoveset
from team import Team, Pokemon
from browser import Selenium, SeleniumException
from log import SimulatorLog
from simulator import Simulator
from gamestate import GameState
from smogon import Smogon
from naive_bayes import get_moves

import sys
import time
import signal
import requests
import json
import re
import traceback
import cPickle as pickle

from agent import OptimisticMinimaxAgent, PessimisticMinimaxAgent, HumanAgent

NAME_CORRECTIONS = {"Keldeo-Resolute": "Keldeo",
                    "Pikachu-Belle": "Pikachu",
                    "Pikachu-Cosplay": "Pikachu",
                    "Pikachu-Libre": "Pikachu",
                    "Pikachu-PhD": "Pikachu",
                    "Pikachu-Pop-Star": "Pikachu",
                    "Pikachu-Rock-Star": "Pikachu",
                    "Meowstic": "Meowstic-M",
                    "Gourgeist-*": "Gourgeist"}
with open("data/graph.json") as fp:
    graph = json.loads(fp.read())

class Showdown():
    def __init__(self, team_text, agent, username, password=None, driver_path="./chromedriver",
                 monitor_url=None):
        self.selenium = Selenium(driver_path=driver_path)
        self.agent = agent
        self.username = username
        self.password = password
        self.team_text = team_text
        self.monitor_url = monitor_url
        with open("data/poke2.json") as f:
            data = f.read()
        with open("data/poke_bw.json") as f2:
            data2 = f2.read()
        poke_data = json.loads(data)
        poke_bw_data = json.loads(data2)
        self.data = Smogon.convert_to_dict(poke_data)
        self.bw_data = Smogon.convert_to_dict(poke_bw_data)
        self.my_team = Team.make_team(team_text, self.data)
        self.opp_team = None
        self.simulator = Simulator()

    def reset(self):
        self.selenium.reset()
        self.opp_team = None
        self.my_team = Team.make_team(self.team_text, self.data)

    def create_initial_gamestate(self):
        my_pokes = self.my_team.copy()
        for i, poke in enumerate(my_pokes.poke_list):
            poke_name = poke.name
            if poke_name in NAME_CORRECTIONS:
                poke_name = NAME_CORRECTIONS[poke_name]
            poke.health = poke.final_stats['hp']
            poke.alive = True
        opp_poke_list = []
        log = SimulatorLog.parse(self.selenium.get_log())
        for event in log.events:
            if event.type == "team" and event.details['username'] != self.username:
                opp_poke_names = event.details['team']
        for name in opp_poke_names:
            if not name:
                continue
            poke_name = name
            if poke_name in NAME_CORRECTIONS:
                poke_name = NAME_CORRECTIONS[poke_name]
            moveset = [m for m in self.data[poke_name].movesets if 'Overused' == m['tag'] or 'Underused' == m['tag'] or 'Rarelyused' == m['tag'] or 'Neverused' == m['tag'] or 'Unreleased' == m['tag'] or 'Ubers' == m['tag']]
            if not len(moveset):
                moveset = [m for m in self.bw_data[poke_name].movesets if 'Overused' == m['tag'] or 'Underused' == m['tag'] or 'Rarelyused' == m['tag'] or 'Neverused' == m['tag'] or 'Unreleased' == m['tag'] or 'Ubers' == m['tag']]
            assert len(moveset), "No candidate movesets for %s" % name
            if len(moveset) > 1:
                moveset = SmogonMoveset.from_dict(moveset[1])
            else:
                moveset = SmogonMoveset.from_dict(moveset[0])
            moves = [x for x in get_moves(poke_name, [], graph) if x != "Hidden Power"][:4]
            moveset.moves = [move[0] for move in moves]
            typing = self.data[poke_name].typing
            stats = self.data[poke_name].stats
            poke = Pokemon(name, typing, stats, moveset, calculate=True)
            poke.health = poke.final_stats['hp']
            poke.alive = True
            opp_poke_list.append(poke)
        for event in log.events:
            if event.type == "switch" and event.player == 0:
                for poke in my_pokes.poke_list:
                    if poke.name == event.poke:
                        my_primary = my_pokes.poke_list.index(poke)
            elif event.type == "switch" and event.player == 1:
                for poke in opp_poke_list:
                    if poke.name == event.poke:
                        opp_primary = opp_poke_list.index(poke)

        self.opp_team = Team(opp_poke_list)
        opp_pokes = self.opp_team.copy()
        my_pokes.primary_poke = my_primary
        opp_pokes.primary_poke = opp_primary

        gamestate = GameState([my_pokes, opp_pokes])
        return gamestate

    def correct_gamestate(self, gamestate):
        my_poke_health = self.selenium.get_my_primary_health()
        opp_poke_health = self.selenium.get_opp_primary_health()
        my_team = gamestate.get_team(0)
        opp_team = gamestate.get_team(1)
        my_team.primary().health = my_poke_health / 100.0 * my_team.primary().final_stats['hp']
        opp_team.primary().health = opp_poke_health / 100.0 * opp_team.primary().final_stats['hp']


    def update_latest_turn(self, gamestate):
        text_log = self.selenium.get_log()
        text_list = text_log.split("\n")
        buffer = []
        turns = []
        for line in text_list:
            line = line.strip()
            if re.match(r"Turn [0-9]+", line):
                turns.append(buffer)
                buffer = []
            else:
                buffer.append(line)
        my_poke = self.selenium.get_my_primary()
        opp_poke = self.selenium.get_opp_primary()
        self.simulator.append_log(gamestate, turns[-1], my_poke=my_poke, opp_poke=opp_poke)

    def init(self):
        self.selenium.start_driver()
        self.selenium.turn_off_sound()
        self.selenium.login(self.username, self.password)
        self.selenium.make_team(self.team_text)

    def update_monitor(self, done=False):
        if self.monitor_url is not None:
            if done:
                status = 'done'
            else:
                status = 'match'
            data = {
                'username': self.username,
                'status': status,
                'scores': self.scores,
                'url': self.battle_url
            }
            try:
                url = self.monitor_url + "/api/update"
                headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
                r = requests.post(url, data=json.dumps(data), headers=headers)
            except:
                pass

    def play_game(self, lobby_game=False):
        self.selenium.choose_tier()
        self.selenium.start_battle()
        self.selenium.wait_for_move()
        self.battle_url = self.selenium.driver.current_url
        self.update_monitor()
        self.selenium.switch_initial(0, 0)
        gamestate = self.create_initial_gamestate()
        self.update_latest_turn(gamestate)
        with open('cur_gs.gs', 'wb') as fp:
            pickle.dump(gamestate, fp)
        over = False
        while not over:
            print "=========================================================================================="
            print "My primary:", gamestate.get_team(0).primary()
            print "Their primary:", gamestate.get_team(1).primary()
            print "Their moves: ", gamestate.get_team(1).primary().moveset.moves
            print "Their item: ", gamestate.get_team(1).primary().item
            print "Their ability: ", gamestate.get_team(1).primary().ability
            print "My move:",
            move = self.agent.get_action(gamestate, 0)

            if move.is_switch():
                self.selenium.switch(move.switch_index, move.backup_switch)
            else:
                self.selenium.move(move.move_index, move.backup_switch, mega=move.mega, volt_turn=move.volt_turn)
            self.update_latest_turn(gamestate)
            self.correct_gamestate(gamestate)

    def run(self, num_games=1):
        self.init()
        self.scores = {
            'wins': 0,
            'losses': 0,
            'crashes': 0
        }
        def signal_handler(signal, frame):
            self.update_monitor(done=True)
            sys.exit(0)
        signal.signal(signal.SIGINT, signal_handler)
        for i in range(num_games):
            self.simulator.log.reset()
            result, error = None, None
            try:
                self.play_game(True)
            except SeleniumException:
                log = SimulatorLog.parse(self.selenium.get_log())
                _, over_event = log.is_over()
                result = over_event.details['username'] == self.username
            except:
                error = traceback.format_exc()
                print "Error", error
            log = self.selenium.get_log()
            id = self.selenium.get_battle_id()
            battle_url = "http://replay.pokemonshowdown.com/battle-%s" % id
            if result == True:
                print "---------------"
                print "Won the battle! - %s" % battle_url
                print "---------------"
                self.scores['wins'] += 1
                with open('logs/wins/%s.log' % id, 'w') as fp:
                    fp.write(log)
            elif result == False:
                print "---------------"
                print "Lost the battle! - %s" % battle_url
                print "---------------"
                self.scores['losses'] += 1
                with open('logs/losses/%s.log' % id, 'w') as fp:
                    fp.write(log)
            else:
                print "---------------"
                print "Crashed! - %s" % id
                print "---------------"
                self.scores['crashes'] += 1
                with open('logs/crashes/%s.log' % id, 'w') as fp:
                    fp.write(log)
                with open('logs/crashes/%s.err' % id, 'w') as fp:
                    fp.write(error)
            self.reset()
        self.update_monitor(done=True)
        self.selenium.close()
        print self.scores





def main():
    from argparse import ArgumentParser
    argparser = ArgumentParser()
    argparser.add_argument('team')
    argparser.add_argument('--username', default='asdf7001')
    argparser.add_argument('--password', default='seleniumpython')
    argparser.add_argument('--iterations', type=int, default=1)
    argparser.add_argument('--monitor_url', type=str, default='http://54.149.105.175:9000')
    args = argparser.parse_args()

    with open(args.team) as fp:
        team_text = fp.read()


    showdown = Showdown(
        team_text,
        PessimisticMinimaxAgent(2),
        args.username,
        password=args.password,
        monitor_url=args.monitor_url
    )
    showdown.run(args.iterations)
