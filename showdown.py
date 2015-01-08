from smogon import SmogonMoveset
from team import Team, Pokemon
from browser import Selenium
from simulator import Simulator
from gamestate import GameState
from smogon import Smogon
import json
import re
import traceback

from agent import OptimisticMinimaxAgent, PessimisticMinimaxAgent

class Showdown():
    def __init__(self, team_text, agent, username, password=None, driver_path="./chromedriver"):
        self.selenium = Selenium(driver_path=driver_path)
        self.agent = agent
        self.username = username
        self.password = password
        self.team_text = team_text
        with open("data/poke2.json") as f:
            data = f.read()
        poke_data = json.loads(data)
        self.data = Smogon.convert_to_dict(poke_data)
        self.my_team = Team.make_team(team_text, self.data)
        self.opp_team = None
        self.simulator = Simulator()

    def create_initial_gamestate(self, my_team, opp_team):
        my_pokes = self.my_team.copy()
        primary = None
        for i, poke in enumerate(my_pokes.poke_list):
            poke_name = poke.name
            if poke_name == "Keldeo-Resolute":
                poke_name = "Keldeo"
            poke.health = my_team[poke_name]['health'] / 100.0 * poke.final_stats['hp']
            poke.alive = my_team[poke_name]['alive']
            if my_team[poke_name]['primary']:
                primary = i
        my_pokes.primary_poke = primary
        if not self.opp_team:
            opp_poke_names = list(opp_team.keys())
            opp_poke_list = []
            for name in opp_poke_names:
                if not name:
                    continue
                poke_name = name
                if name == "Keldeo-Resolute":
                    poke_name = "Keldeo"
                moveset = [m for m in self.data[poke_name].movesets if 'Overused' == m['tag'] or 'Underused' == m['tag'] or 'Rarelyused' == m['tag'] or 'Neverused' == m['tag'] or 'Unreleased' == m['tag'] or 'Ubers' == m['tag']]
                assert len(moveset), "No candidate movesets for %s" % name
                if len(moveset) >= 2 and poke_name != "Latios":
                    moveset = SmogonMoveset.from_dict(moveset[1])
                else:
                    moveset = SmogonMoveset.from_dict(moveset[0])
                moveset.moves = moveset.moves[:4]
                typing = self.data[poke_name].typing
                stats = self.data[poke_name].stats
                poke = Pokemon(name, typing, stats, moveset, calculate=True)
                opp_poke_list.append(poke)

            self.opp_team = Team(opp_poke_list)

        opp_pokes = self.opp_team.copy()
        primary = None
        for i, poke in enumerate(opp_pokes.poke_list):
            poke.health = opp_team[poke.name]['health'] / 100.0 * poke.final_stats['hp']
            poke.alive = opp_team[poke.name]['alive']
            if opp_team[poke.name]['primary']:
                primary = i
        opp_pokes.primary_poke = primary

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
        opp_poke = self.selenium.get_opp_primary()
        self.simulator.append_log(gamestate, turns[-1], opp_poke=opp_poke)

    def init(self):
        self.selenium.start_driver()
        self.selenium.turn_off_sound()
        self.selenium.login(self.username, self.password)
        self.selenium.make_team(self.team_text)
        self.selenium.choose_tier()

    def play_game(self):
        print "Starting battle"
        self.selenium.start_battle()
        print "Waiting for move"
        self.selenium.wait_for_move()
        print "Selecting first pokemon"
        self.selenium.move(0, 0)
        my_team = self.selenium.get_my_team()
        opp_team = self.selenium.get_opp_team()
        gamestate = self.create_initial_gamestate(my_team, opp_team)
        self.update_latest_turn(gamestate)
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
            over, over_event = self.simulator.log.is_over()
        return over_event.details['username'] == self.username


    def run(self, num_games=1):
        print "Init"
        self.init()
        for i in range(num_games):
            self.simulator.log.reset()
            result, error = None, None
            try:
                print "Playing game"
                result = self.play_game()
            except:
                error = traceback.format_exc()
                print "Error", error

            print "Getting log"
            log = self.selenium.get_log()
            id = self.selenium.get_battle_id()
            if result == True:
                with open('logs/wins/%s.log' % id, 'w') as fp:
                    fp.write(log)
            elif result == False:
                with open('logs/losses/%s.log' % id, 'w') as fp:
                    fp.write(log)
            else:
                with open('logs/crashes/%s.log' % id, 'w') as fp:
                    fp.write(log)
                with open('logs/crashes/%s.err' % id, 'w') as fp:
                    fp.write(error)
            print "Resetting"
            self.selenium.reset()
        self.selenium.close()






if __name__ == "__main__":
    from argparse import ArgumentParser
    argparser = ArgumentParser()
    argparser.add_argument('team')
    argparser.add_argument('--username', default='asdf8000')
    argparser.add_argument('--password', default='seleniumpython')
    argparser.add_argument('--iterations', type=int, default=1)
    args = argparser.parse_args()

    with open(args.team) as fp:
        team_text = fp.read()


    showdown = Showdown(
        team_text,
        PessimisticMinimaxAgent(2),
        args.username,
        password=args.password,
    )
    showdown.run(args.iterations)
