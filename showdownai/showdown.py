from smogon import SmogonMoveset
from team import Team, Pokemon
from browser import Selenium
from log import SimulatorLog
from simulator import Simulator
from gamestate import GameState
from agent import PessimisticMinimaxAgent
from data import NAME_CORRECTIONS, MOVE_CORRECTIONS, load_data, get_move, correct_name, get_hidden_power
from move_predict import create_predictor
from path import Path
from exceptions import *
from state import KernelState
import time

import sys
import platform
import signal
import requests
import json
import re
import traceback
import logging

KERNEL_STATE = "state.json"

OS_MAP = {
    '64bit' : {
        'ELF' : 'linux64'
    },
    '32bit': {
        'ELF' : 'linux32'
    }
}

class Showdown():
    def __init__(self, team_text, agent, username, pokedata, password=None,
                 monitor_url=None, proxy=False, browser='phantomjs', predictor_name='PokeFrequencyPredictor',
                 verbose=False, kernel_dir="kernel", kernel=False, lib_dir="lib"):
        self.logger = logging.getLogger("showdown")
        self.logger.setLevel(level=logging.INFO)
        self.agent = agent
        self.username = username
        self.password = password
        self.team_text = team_text
        self.predictor_name = predictor_name
        self.monitor_url = monitor_url
        self.battle_url = None
        self.pokedata = pokedata
        self.smogon_data = pokedata.smogon_data
        self.smogon_bw_data = pokedata.smogon_bw_data
        self.graph_move = pokedata.graph_move
        self.graph_poke = pokedata.graph_poke
        self.poke_moves = pokedata.poke_moves
        self.my_team = Team.make_team(team_text, self.smogon_data)
        self.opp_team = None
        self.simulator = Simulator(pokedata)
        arch = platform.architecture()
        self.lib_dir = Path(lib_dir) / OS_MAP[arch[0]][arch[1]]
        self.selenium = Selenium(proxy=proxy, browser=browser, lib_dir=self.lib_dir)
        self.verbose = verbose
        self.kernel_dir = Path(kernel_dir)
        self.kernel = kernel
        if self.kernel and not self.kernel_dir.exists():
            self.kernel_dir.mkdir()
        self.state = KernelState(self.kernel_dir / KERNEL_STATE, self.kernel)
        self.state.update_state("status", "idle")
        if self.verbose:
            self.logger.setLevel(level=logging.DEBUG)

    def reset(self):
        self.state.update_state("status", "idle")
        self.logger.info("Resetting...")
        self.simulator.score = 0
        self.simulator.total = 0
        self.selenium.reset()
        self.opp_team = None
        self.my_team = Team.make_team(self.team_text, self.smogon_data)

    def create_initial_gamestate(self):
        self.logger.info("Creating initial gamestate...")
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
            poke_name = correct_name(name)
            "Corrected to:", poke_name
            if poke_name in self.smogon_data:
                moveset = [m for m in self.smogon_data[poke_name].movesets if 'Overused' == m['tag'] or 'Underused' == m['tag'] or 'Rarelyused' == m['tag'] or 'Neverused' == m['tag'] or 'Unreleased' == m['tag'] or 'Ubers' == m['tag'] or 'PU' in m['tag']]
                if len(moveset) > 1:
                    moveset = SmogonMoveset.from_dict(moveset[1])
                elif len(moveset) == 1:
                    moveset = SmogonMoveset.from_dict(moveset[0])
                else:
                    moveset = [m for m in self.smogon_bw_data[poke_name].movesets if 'Overused' == m['tag'] or 'Underused' == m['tag'] or 'Rarelyused' == m['tag'] or 'Neverused' == m['tag'] or 'Unreleased' == m['tag'] or 'Ubers' == m['tag'] or 'PU' in m['tag']]
                    moveset = SmogonMoveset.from_dict(moveset[0])
            elif poke_name not in self.smogon_data and poke_name in self.smogon_bw_data:
                moveset = [m for m in self.smogon_bw_data[poke_name].movesets if 'Overused' == m['tag'] or 'Underused' == m['tag'] or 'Rarelyused' == m['tag'] or 'Neverused' == m['tag'] or 'Unreleased' == m['tag'] or 'Ubers' == m['tag'] or 'PU' in m['tag']]
                moveset = SmogonMoveset.from_dict(moveset[0])
            else:
                moveset = SmogonMoveset(None, None, None, {'hp': 88, 'patk': 84, 'pdef': 84, 'spatk': 84, 'spdef': 84, 'spe': 84}, {'hp': 1.0, 'patk': 1.0, 'pdef': 1.0, 'spatk': 1.0, 'spdef': 1.0, 'spe': 1.0}, None, 'ou')
            moveset.moves = None
            if poke_name in self.smogon_data:
                typing = self.smogon_data[poke_name].typing
                stats = self.smogon_data[poke_name].stats
            elif poke_name not in self.smogon_data and poke_name in self.smogon_bw_data:
                typing = self.smogon_bw_data[poke_name].typing
                stats = self.smogon_bw_data[poke_name].stats
            else:
                typing = ['Normal']
                stats = {'hp': 80, 'patk': 80, 'pdef': 80, 'spatk': 80, 'spdef': 80, 'spe': 80}
            predictor = create_predictor(self.predictor_name, name, self.pokedata)
            poke = Pokemon(name, typing, stats, moveset, predictor, calculate=True)
            moves = [x[0] for x in poke.predict_moves([])]
            poke.moveset.moves = moves[:4]
            poke.health = poke.final_stats['hp']
            poke.alive = True
            opp_poke_list.append(poke)
        my_primary = None
        for event in log.events:
            if event.type == "switch" and event.player == 0:
                for poke in my_pokes.poke_list:
                    if poke.name == event.poke:
                        my_primary = my_pokes.poke_list.index(poke)
            elif event.type == "switch" and event.player == 1:
                for poke in opp_poke_list:
                    if poke.name == event.poke:
                        opp_primary = opp_poke_list.index(poke)

        assert my_primary != None
        self.opp_team = Team(opp_poke_list)
        opp_pokes = self.opp_team.copy()
        my_pokes.primary_poke = my_primary
        opp_pokes.primary_poke = opp_primary

        gamestate = GameState([my_pokes, opp_pokes])
        return gamestate

    def correct_gamestate(self, gamestate):
        self.logger.info("Correcting Pokemon health...")
        gamestate = gamestate.deep_copy()
        my_poke_health = self.selenium.get_my_primary_health()
        opp_poke_health = self.selenium.get_opp_primary_health()
        my_team = gamestate.get_team(0)
        opp_team = gamestate.get_team(1)
        my_team.primary().health = my_poke_health / 100.0 * my_team.primary().final_stats['hp']
        opp_team.primary().health = opp_poke_health / 100.0 * opp_team.primary().final_stats['hp']
        return gamestate


    def update_latest_turn(self, gamestate):
        self.logger.info("Updating with latest information...")
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
            my_move = move_events[1].details['move']
            opp_move = move_events[0].details['move']
            if my_move == "Hidden Power":
                my_move = get_hidden_power(move_events[1].poke, self.smogon_data)
            if opp_move == "Hidden Power":
                opp_move = get_hidden_power(move_events[0].poke, self.smogon_data)
            if my_move in MOVE_CORRECTIONS:
                my_move = MOVE_CORRECTIONS[my_move]
            if opp_move in MOVE_CORRECTIONS:
                opp_move = MOVE_CORRECTIONS[opp_move]
            my_move = get_move(my_move)
            opp_move = get_move(opp_move)
            if move_events[0].player != self.simulator.get_first(old_gamestate, [my_move, opp_move], 0):
                opp_poke = old_gamestate.get_team(1).primary()
                for poke in gamestate.get_team(1).poke_list:
                    if poke.name == opp_poke.name:
                        poke.item = "Choice Scarf"
        return gamestate

    def init(self):
        self.logger.info("Initializing showdown")
        self.selenium.start_driver()
        self.selenium.clear_cookies()
        self.selenium.screenshot('log.png')
        self.selenium.turn_off_sound()
        self.selenium.login(self.username, self.password)
        self.selenium.screenshot('log.png')
        self.selenium.make_team(self.team_text)
        self.selenium.screenshot('log.png')

    def update_monitor(self, done=False):
        if self.monitor_url is not None:
            self.logger.info("Updating online monitor at: %s",
                             self.monitor_url)
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
                requests.post(url, data=json.dumps(data), headers=headers)
            except:
                pass

    def play_game(self, challenge=None):
        self.state.update_state("status", "finding_game")
        self.logger.info("Finding a game...")
        self.selenium.screenshot('log.png')
        tier_click = False
        while not tier_click:
            try:
                self.selenium.choose_tier()
                self.selenium.screenshot('log.png')
                if challenge:
                    self.selenium.start_challenge_battle(challenge)
                else:
                    self.selenium.start_ladder_battle()
                self.selenium.screenshot('log.png')
                tier_click = True
            except TierException:
                self.logger.warning("Unable to click tier. Trying again...")
            self.selenium.screenshot('log.png')
            self.battle_url = self.selenium.driver.current_url
            self.selenium.screenshot('log.png')
            self.logger.info("Found game: %s", self.battle_url)
            self.state.update_state("status", "in_battle")
            self.state.update_state("battle_url", self.battle_url)
            self.update_monitor()
            self.selenium.wait_for_move()
            self.selenium.chat("gl hf!")
            self.selenium.switch_initial(0, 0)
            self.selenium.screenshot('log.png')
            gamestate = self.create_initial_gamestate()
            gamestate = self.update_latest_turn(gamestate)
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
                self.selenium.screenshot('log.png')
        self.state.delete_state("battle_url")

    def run(self, num_games=1, challenge=None):
        self.state.update_state("status", "initializing_battle")
        if challenge:
            self.logger.info("Set to challenge: %s", challenge)
        else:
            self.logger.info("Set to play %u games", num_games)
        self.init()
        self.scores = {
            'wins': 0,
            'losses': 0,
            'crashes': 0
        }
        def signal_handler(signal, frame):
            self.update_monitor(done=True)
            sys.exit(0)
        #signal.signal(signal.SIGINT, signal_handler)
        for i in range(num_games):
            self.simulator.log.reset()
            result, error = None, None
            try:
                self.play_game(challenge=challenge)
            except GameOverException:
                log = SimulatorLog.parse(self.selenium.get_log())
                disconnected = log.disconnected()
                if disconnected:
                    over,_ = log.is_over()
                    while not over:
                        time.sleep(5)
                        over,_ = log.is_over()
                _, over_event = log.is_over()
                result = over_event.details['username'] == self.username
            except UserNotOnlineException:
                self.logger.error("User not online: %s", challenge)
                self.logger.info("Exiting...")
                return
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
            self.logger.info("Finished game! Replay can be found at: %s", battle_url)
            user_folder = Path(".") / self.username
            if not user_folder.exists():
                user_folder.mkdir()
            if not (user_folder / "wins").exists():
                (user_folder / "wins").mkdir()
            if not (user_folder / "losses").exists():
                (user_folder / "losses").mkdir()
            if not (user_folder / "crashes").exists():
                (user_folder / "crashes").mkdir()
            if result == True:
                print "---------------"
                print "Won the battle! - %s" % battle_url
                print "---------------"
                self.scores['wins'] += 1
                with open(user_folder / "wins" / ("%s.log" % id), 'w') as fp:
                    fp.write(log)
                with open(user_folder / "wins" / ("%s.score" % id), 'w') as fp:
                    print >>fp, self.simulator.score
                    print >>fp, self.simulator.total
            elif result == False:
                print "---------------"
                print "Lost the battle! - %s" % battle_url
                print "---------------"
                self.scores['losses'] += 1
                with open(user_folder / "losses" / ("%s.log" % id), 'w') as fp:
                    fp.write(log)
                with open(user_folder / "losses" / ("%s.score" % id), 'w') as fp:
                    print >>fp, self.simulator.score
                    print >>fp, self.simulator.total
            else:
                print "---------------"
                print "Crashed! - %s" % id
                print "---------------"
                self.scores['crashes'] += 1
                with open(user_folder / "crashes" / ("%s.log" % id), 'w') as fp:
                    fp.write(log)
                with open(user_folder / "crashes" / ("%s.err" % id), 'w') as fp:
                    fp.write(error)
                with open(user_folder / "crashes" / ("%s.score" % id), 'w') as fp:
                    print >>fp, self.simulator.score
                    print >>fp, self.simulator.total
            events = SimulatorLog.parse(self.selenium.get_log())
            for event in events:
                if event.type == "ladder":
                    if event.details['username'] == self.username:
                        with open(user_folder / "ladder_ratings.txt", "a") as fp:
                            fp.write(event.details['ladder'] + "\n")
            self.reset()
        self.update_monitor(done=True)
        self.selenium.close()
        self.logger.info("Done!")


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
    argparser.add_argument('--browser', type=str, default='phantomjs')
    argparser.add_argument('--data_dir', type=str, default='data/')
    argparser.add_argument('--lib_dir', type=str, default='lib/')
    argparser.add_argument('--kernel_dir', type=str, default='kernel/')
    argparser.add_argument('--kernel', action='store_true')
    argparser.add_argument('--predictor', default='PokeFrequencyPredictor')
    argparser.add_argument("-v", "--verbose", help="increase output verbosity",
                                            action="store_true")
    args = argparser.parse_args()

    with open(args.team) as fp:
        team_text = fp.read()


    pokedata = load_data(args.data_dir)

    showdown = Showdown(
        team_text,
        OptimisticMinimax(2, pokedata),
        args.username,
        pokedata,
        password=args.password,
        proxy=args.proxy,
        browser=args.browser,
        monitor_url=args.monitor_url,
        predictor_name=args.predictor,
        verbose=args.verbose,
        data_dir=args.data_dir,
        lib_dir=args.lib_dir,
        kernel_dir=args.kernel_dir,
        kernel=args.kernel
    )
    showdown.run(args.iterations, challenge=args.challenge)
