import re
import json
from path import path
directory = path('.')
USER_PLAYER = r"\|player\|(?P<player>.+?)\|(?P<username>.+?)\|.*?"
POKE = r"\|poke\|p(?P<player>.+?)\|(?P<poke>.+)"
SWITCH = r"\|switch\|p(?P<player>.+?)a: (?P<nickname>.+?)\|(?P<pokename>.+)\|.+?"
DRAG = r"\|drag\|p(?P<player>.+?)a: (?P<nickname>.+?)\|(?P<pokename>.+)\|.+?"
MOVE = r"\|move\|p(?P<player>.+?)a: (?P<poke>.+?)\|(?P<move>.+?)\|.+?"
MOVE_CORRECTIONS = {"ExtremeSpeed": "Extreme Speed",
                    "ThunderPunch": "Thunder Punch",
                    "SolarBeam": "Solar Beam",
                    "DynamicPunch": "Dynamic Punch"}

def handle_line(username, line):
    line = line.strip()
    match = re.match(USER_PLAYER, line)
    if match:
        if match.group("player") == "p1" and match.group("username").lower() != username.lower():
            global player
            player = "1"
        elif match.group("player") == "p2" and match.group("username").lower() != username.lower():
            global player
            player = "2"
    match = re.match(POKE, line)
    if match:
        if player == match.group("player"):
            poke = match.group("poke").split(",")[0]
            if poke == "Zoroark":
                raise Zoroark()
            if poke == "Zorua":
                raise Zoroark()
            if "Keldeo" in poke:
                poke = "Keldeo"
            opp_team[poke] = []
    match = re.match(SWITCH, line)
    if match:
        if player == match.group("player"):
            nickname = match.group("nickname")
            pokename = match.group("pokename").split(",")[0]
            if "-Mega" in pokename:
                pokename = pokename[:-5]
            if pokename == "Charizard-M":
                pokename = "Charizard"
            if "Gourgeist" in pokename:
                for name in opp_team:
                    if "Gourgeist" in name:
                        gourgeist = name
                opp_team[pokename] = opp_team[gourgeist]
            if "Keldeo" in pokename:
                pokename = "Keldeo"
            if "Keldeo" in nickname:
                nickname = "Keldeo"
            opp_nicknames[nickname] = pokename
    match = re.match(DRAG, line)
    if match:
        if player == match.group("player"):
            nickname = match.group("nickname")
            pokename = match.group("pokename").split(",")[0]
            if "-Mega" in pokename:
                pokename = pokename[:-5]
            if pokename == "Charizard-M":
                pokename = "Charizard"
            if "Keldeo" in pokename:
                pokename = "Keldeo"
            if "Keldeo" in nickname:
                nickname = "Keldeo"
            opp_nicknames[nickname] = pokename
    match = re.match(MOVE, line)
    if match:
        poke = match.group("poke")
        if "Keldeo" in poke:
            poke = "Keldeo"
        if player == match.group("player"):
            if match.group("move") not in opp_team[opp_nicknames[poke]]:
                opp_team[opp_nicknames[poke]].append(match.group("move"))

def make_graph_move(opp_team, graph_move, graph_move_frequencies):
    for poke in opp_team:
        for move in opp_team[poke]:
            if move in MOVE_CORRECTIONS:
                move = MOVE_CORRECTIONS[move]
            if move not in graph_move_frequencies:
                graph_move_frequencies[move] = 0
            if move not in graph_move:
                graph_move[move] = {}
            graph_move_frequencies[move] += 1
            for othermove in opp_team[poke]:
                if othermove in MOVE_CORRECTIONS:
                    othermove = MOVE_CORRECTIONS[othermove]
                if move == othermove:
                    continue
                if othermove in graph_move[move]:
                    graph_move[move][othermove] += 1
                else:
                    graph_move[move][othermove] = 1
    return graph_move, graph_move_frequencies


def make_graph_poke(opp_team, graph_poke, graph_frequencies):
    for poke in opp_team:
        if poke not in graph_poke:
            graph_poke[poke] = {}
        if poke not in graph_frequencies:
            graph_frequencies[poke] = {}
        for move in opp_team[poke]:
            if move in MOVE_CORRECTIONS:
                move = MOVE_CORRECTIONS[move]
            if move not in graph_poke[poke]:
                graph_poke[poke][move] = {}
            if move not in graph_frequencies[poke]:
                graph_frequencies[poke][move] = 0
            graph_frequencies[poke][move] += 1
            for othermove in opp_team[poke]:
                if othermove in MOVE_CORRECTIONS:
                    othermove = MOVE_CORRECTIONS[othermove]
                if move == othermove:
                    continue
                if othermove in graph_poke[poke][move]:
                    graph_poke[poke][move][othermove] += 1
                else:
                    graph_poke[poke][move][othermove] = 1
    return graph_poke, graph_frequencies

class Zoroark(Exception):
    pass

if __name__ == "__main__":
    graph_poke = {}
    graph_move = {}
    graph_move_frequencies = {}
    graph_frequencies = {}
    names = path("./uu/logs").listdir() + path('./ou/logs').listdir()
    for username in names:
        directory = username
        for log in directory.files():
            if "uu-186975396" in log or "uu-197134198" in log or "uu-202631332" in log or "uu-190650459" in log or "ou-203216292" in log or "ou-202070019" in log or "ou-147740692" in log:
                continue
            if "gen4" in log or "gen3" in log or "gen2" in log or "gen1" in log or "pandora" in log:
                continue
            if "uu-" not in log and "ou-" not in log:
                continue
            print log
            player = ""
            opp_team = {}
            opp_nicknames = {}
            with open("%s" % log) as f:
                log = f.read()
            user = directory.name
            lines = log.split("\n")
            skip = False
            for line in lines:
                try:
                    handle_line(user, line)
                except Zoroark:
                    skip = True
                    break
            if skip:
                continue
            graph_poke, graph_move_frequencies = make_graph_poke(opp_team, graph_poke, graph_move_frequencies)
    poke_graph = {
        'frequencies': graph_move_frequencies,
        'cooccurences': graph_poke,
    }
    with open("graph_move.json", "w") as f:
        f.write(json.dumps(poke_graph, sort_keys=True,indent=4, separators=(',', ': ')))
