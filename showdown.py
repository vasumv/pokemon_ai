from smogon import SmogonMoveset
from team import Team, Pokemon
from runner import Selenium, SeleniumLog
from simulator import Simulator, Action
from gamestate import GameState
from smogon import Smogon
import json

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
            poke.health = my_team[poke_name]['health'] / 100.0 * poke.final_stats['hp']
            poke.alive = my_team[poke_name]['alive']
            if my_team[poke_name]['primary']:
                primary = i
        my_pokes.primary_poke = primary
        if not self.opp_team:
            opp_poke_names = list(opp_team.keys())
            opp_poke_list = []
            for name in opp_poke_names:
                poke_name = poke.name
                if poke.name[-5:] == "-Mega":
                    poke_name = poke.name[:-5]
                moveset = [m for m in self.data[name].movesets if 'Overused' == m['tag'] or 'Underused' == m['tag'] or 'Rarelyused' == m['tag'] or 'Neverused' == m['tag'] or 'Unreleased' == m['tag'] or 'Ubers' == m['tag']]
                assert len(moveset), "No candidate movesets for %s" % name
                if len(moveset) >= 2:
                    moveset = SmogonMoveset.from_dict(moveset[1])
                else:
                    moveset = SmogonMoveset.from_dict(moveset[0])
                typing = self.data[name].typing
                stats = self.data[name].stats
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

    def create_gamestate(self, my_team, opp_team):
        my_pokes = self.my_team.copy()
        primary = None
        for i, poke in enumerate(my_pokes.poke_list):
            poke_name = poke.name
            if poke.name[-5:] == "-Mega":
                poke_name = poke.name[:-5]
            if poke.name[-7:] == "-Mega-X" or poke.name[-7:] == "-Mega-Y":
                poke_name = poke.name[:-7]
            poke.health = my_team[poke_name]['health'] / 100.0 * poke.final_stats['hp']
            poke.alive = my_team[poke_name]['alive']
            if my_team[poke_name]['primary']:
                primary = i
        my_pokes.primary_poke = primary

        if not self.opp_team:
            opp_poke_names = list(opp_team.keys())
            opp_poke_list = []
            for name in opp_poke_names:
                poke_name = poke.name
                if poke.name[-5:] == "-Mega":
                    poke_name = poke.name[:-5]
                moveset = [m for m in self.data[name].movesets if 'Overused' == m['tag'] or 'Underused' == m['tag'] or 'Rarelyused' == m['tag'] or 'Neverused' == m['tag'] or 'Unreleased' == m['tag'] or 'Ubers' == m['tag']]
                assert len(moveset), "No candidate movesets for %s" % name
                if len(moveset) >= 2:
                    moveset = SmogonMoveset.from_dict(moveset[1])
                else:
                    moveset = SmogonMoveset.from_dict(moveset[0])
                typing = self.data[name].typing
                stats = self.data[name].stats
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

    def start(self):
        self.selenium.start_driver()
        self.selenium.turn_off_sound()
        self.selenium.login(self.username, self.password)
        self.selenium.make_team(self.team_text)
        self.selenium.start_battle()
        self.selenium.wait_for_move()
        self.selenium.move(0, 0)
        while True:
            my_team = self.selenium.get_my_team()
            opp_team = self.selenium.get_opp_team()
            gamestate = self.create_gamestate(my_team, opp_team)
            print "=========================================================================================="
            print "My primary:", gamestate.get_team(0).primary()
            print "Their primary:", gamestate.get_team(1).primary()
            print "Their moves: ", gamestate.get_team(1).primary().moveset.moves
            print "Their item: ", gamestate.get_team(1).primary().moveset.item
            print "Their ability: ", gamestate.get_team(1).primary().ability
            print "My move:",
            move = self.agent.get_action(gamestate, 0)
            their = (gamestate.get_legal_actions(1))[0]
            print
            next = self.simulator.simulate(gamestate, [move, their], 0, log=True)
            self.my_team = next.get_team(0)
            self.opp_team = next.get_team(1)

            if move.is_switch():
                self.selenium.switch(move.switch_index, move.backup_switch)
            else:
                self.selenium.move(move.move_index, move.backup_switch, mega=move.mega, volt_turn=move.volt_turn)



if __name__ == "__main__":
    with open('teams/pokemon_team2.txt') as fp:
        team_text = fp.read()


    showdown = Showdown(
        team_text,
        PessimisticMinimaxAgent(2),
        "asdf8000",
        password="seleniumpython"
    )
    showdown.start()
