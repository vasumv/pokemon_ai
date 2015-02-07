from smogon import SmogonMoveset
from team import Team, Pokemon
from browser import Selenium, SeleniumException
from log import SimulatorLog
from simulator import Simulator
from gamestate import GameState
from smogon import Smogon
from agent import OptimisticMinimaxAgent, PessimisticMinimaxAgent, HumanAgent
from naive_bayes import get_moves
from data import NAME_CORRECTIONS, load_data, get_move
from move_predict import create_predictor

import sys
import time
import signal
import requests
import json
import re
import traceback
import cPickle as pickle

class Showdown():
    def __init__(self, team_text, agent, username, pokedata, password=None, driver_path="./chromedriver",
                 monitor_url=None, proxy=False, firefox=False, predictor_name='FrequencyPokePredictor'):
        self.selenium = Selenium(driver_path=driver_path, proxy=proxy, firefox=firefox)
        self.agent = agent
        self.username = username
        self.password = password
        self.team_text = team_text
        self.predictor_name = predictor_name
        self.monitor_url = monitor_url
        self.pokedata = pokedata
        self.smogon_data = pokedata.smogon_data
        self.smogon_bw_data = pokedata.smogon_bw_data
        self.graph = pokedata.graph
        self.graph_poke = pokedata.graph_poke
        self.poke_moves = pokedata.poke_moves
        self.my_team = Team.make_team(team_text, self.smogon_data)
        self.opp_team = None
        self.simulator = Simulator(pokedata)

    def reset(self):
        self.score = 0
        self.selenium.reset()
        self.opp_team = None
        self.my_team = Team.make_team(self.team_text, self.smogon_data)

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
            moveset = [m for m in self.smogon_data[poke_name].movesets if 'Overused' == m['tag'] or 'Underused' == m['tag'] or 'Rarelyused' == m['tag'] or 'Neverused' == m['tag'] or 'Unreleased' == m['tag'] or 'Ubers' == m['tag']]
            if not len(moveset):
                moveset = [m for m in self.bw_data[poke_name].movesets if 'Overused' == m['tag'] or 'Underused' == m['tag'] or 'Rarelyused' == m['tag'] or 'Neverused' == m['tag'] or 'Unreleased' == m['tag'] or 'Ubers' == m['tag']]
            assert len(moveset), "No candidate movesets for %s" % name
            if len(moveset) > 1:
                moveset = SmogonMoveset.from_dict(moveset[1])
            else:
                moveset = SmogonMoveset.from_dict(moveset[0])
            moveset.moves = None
            typing = self.smogon_data[poke_name].typing
            stats = self.smogon_data[poke_name].stats
            predictor = create_predictor(self.predictor_name, name, self.pokedata)
            poke = Pokemon(name, typing, stats, moveset, predictor, calculate=True)
            moves = [x[0] for x in poke.predict_moves([])]
            poke.moveset.moves = moves[:4]
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
        gamestate = gamestate.deep_copy()
        my_poke_health = self.selenium.get_my_primary_health()
        opp_poke_health = self.selenium.get_opp_primary_health()
        my_team = gamestate.get_team(0)
        opp_team = gamestate.get_team(1)
        my_team.primary().health = my_poke_health / 100.0 * my_team.primary().final_stats['hp']
        opp_team.primary().health = opp_poke_health / 100.0 * opp_team.primary().final_stats['hp']
        return gamestate


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
        my_poke_name = self.selenium.get_my_primary()
        opp_poke_name = self.selenium.get_opp_primary()

        old_gamestate = gamestate
        gamestate = gamestate.deep_copy()

        self.simulator.append_log(gamestate, turns[-1], my_poke=my_poke_name, opp_poke=opp_poke_name)
        move_events = []
        for event in self.simulator.latest_turn:
            if event.type == "move":
                move_events.append(event)
        if len(move_events) == 2 and move_events[0].player == 1:
            if move_events[0].player != self.simulator.get_first(old_gamestate, [get_move(move_events[0].details['move']), get_move(move_events[1].details['move'])], 0):
                opp_poke = old_gamestate.get_team(1).primary()
                for poke in gamestate.get_team(1).poke_list:
                    if poke.name == opp_poke.name:
                        poke.item = "Choice Scarf"
        return gamestate



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

    def play_game(self, challenge=None):
        self.selenium.choose_tier()
        if challenge:
            self.selenium.start_challenge_battle(challenge)
        else:
            self.selenium.start_ladder_battle()
        self.selenium.wait_for_move()
        self.battle_url = self.selenium.driver.current_url
        self.update_monitor()
        self.selenium.switch_initial(0, 0)
        gamestate = self.create_initial_gamestate()
        gamestate = self.update_latest_turn(gamestate)
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
            gamestate = self.update_latest_turn(gamestate)
            gamestate = self.correct_gamestate(gamestate)

    def run(self, num_games=1, challenge=None):
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
                self.play_game(challenge=challenge)
            except SeleniumException:
                log = SimulatorLog.parse(self.selenium.get_log())
                _, over_event = log.is_over()
                result = over_event.details['username'] == self.username
            except:
                error = traceback.format_exc()
                print "Error", error
                log = SimulatorLog.parse(self.selenium.get_log())
                _, over_event = log.is_over()
                if over_event is not None:
                    result = over_event.details['username'] == self.username
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
            print self.simulator.score, self.simulator.total
            with open('logs/%s-score.txt' % id, 'w') as fp:
                print >>fp, self.simulator.score
                print >>fp, self.simulator.total
            events = SimulatorLog.parse(self.selenium.get_log())
            for event in events:
                if event.type == "ladder":
                    if event.details['username'] == self.username:
                        with open("ladder_ratings.txt", "a") as fp:
                            fp.write(event.details['ladder'] + "\n")
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
    argparser.add_argument('--challenge', type=str)
    argparser.add_argument('--proxy', action='store_true')
    argparser.add_argument('--firefox', action='store_true')
    argparser.add_argument('--data_dir', type=str, default='data/')
    argparser.add_argument('--predictor', default='FrequencyPokePredictor')
    args = argparser.parse_args()

    with open(args.team) as fp:
        team_text = fp.read()

    pokedata = load_data(args.data_dir)

    showdown = Showdown(
        team_text,
        PessimisticMinimaxAgent(2, pokedata),
        args.username,
        pokedata,
        password=args.password,
        proxy=args.proxy,
        firefox=args.firefox,
        monitor_url=args.monitor_url,
        predictor_name=args.predictor
    )
    showdown.run(args.iterations, challenge=args.challenge)
