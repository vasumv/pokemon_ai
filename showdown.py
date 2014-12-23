from smogon import SmogonMoveset
from team import Team, Pokemon
from runner import Selenium
from simulator import Simulator
from gamestate import GameState
from smogon import Smogon
import json
import time
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
    def create_gamestate(self, my_team, opp_team):
        my_pokes = self.my_team.copy()
        primary = None
        for i, poke in enumerate(my_pokes.poke_list):
            poke.health = my_team[poke.name]['health']
            poke.alive = my_team[poke.name]['alive']
            if my_team[poke.name]['primary']:
                primary = i
        my_pokes.primary_poke = primary

        opp_poke_names = list(opp_team.keys())
        opp_poke_list = []
        for name in opp_poke_names:
            moveset = [m for m in self.data[name].movesets if 'Overused' == m['tag'] or 'Underused' == m['tag'] or 'Rarelyused' == m['tag'] or 'Neverused' in m['tag']]
            assert len(moveset), "No candidate movesets for %s" % name
            moveset = moveset[0]
            typing = self.data[name].typing
            stats = self.data[name].stats
            poke = Pokemon(name, typing, stats, moveset)
            opp_poke_list.append(poke)

        opp_pokes = Team(opp_poke_list)
        primary = None
        for i, poke in enumerate(opp_poke_list):
            poke.health = opp_team[poke]['health']
            poke.alive = opp_team[poke]['alive']
            if opp_team[poke]['primary']:
                primary = i
        opp_pokes.primary_poke = primary


        gamestate = GameState(my_pokes, opp_pokes)
        return gamestate

    def start(self):
        self.selenium.start_driver()
        self.selenium.turn_off_sound()
        self.selenium.login(self.username, self.password)
        self.selenium.make_team(self.team_text)
        self.selenium.start_battle()
        time.sleep(14)
        self.selenium.switch(0, 3)
        my_team = self.selenium.get_my_team()
        opp_team = self.selenium.get_opp_team()
        print my_team
        print opp_team
        g = self.create_gamestate(my_team, opp_team)
        print g.my_team, g.opp_team
        move = self.agent(g)




if __name__ == "__main__":
    with open('teams/overpowered.txt') as fp:
        team_text = fp.read()

    from game import get_pess_action

    showdown = Showdown(
        team_text,
        get_pess_action,
        "asdf7000",
        password="seleniumpython"
    )
    showdown.start()
