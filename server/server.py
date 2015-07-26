from flask import Flask, jsonify, send_from_directory, render_template
from webargs import Arg
from webargs.flaskparser import use_args
from showdownai import Showdown
from showdownai import PessimisticMinimaxAgent
from showdownai import load_data
from argparse import ArgumentParser
from path import Path
from threading import Thread, Timer
import webbrowser

class Server():

    def __init__(self, teamdir, datadir):
        self.teamdir = Path(teamdir)
        self.datadir = datadir
        self.pokedata = load_data(datadir)
        self.ids = {}
        self.counter = 0
        self.app = app = Flask(__name__, static_url_path='',
                               static_folder='static',
                               template_folder='templates')

        @app.route("/")
        def index():
            files = self.get_team_files()
            return render_template('index.html', teamfiles=files)

        @app.route("/bots")
        def bots():
            return render_template('bots.html')

        @app.route("/api/showdown/<int:id>", methods=['get'])
        def get_showdown(id):
            showdownobj = self.ids[id]
            url = showdownobj.battle_url
            showdownargs = {
                'id': id,
                'url': url
            }
            return jsonify(**showdownargs)

        @app.route("/api/play_game", methods=['get', 'post'])
        @use_args({
            'iterations': Arg(int, default=1),
            'username': Arg(str, required=True),
            'password': Arg(str, required=True),
            'teamfile': Arg(str, required=True),
            'teamtext': Arg(str, required=True),
            'challenge': Arg(str, default=None),
            'browser': Arg(str, default="phantomjs"),
        })
        def play_game(args):
            if args['teamtext'] != "":
                team_text = args['team_text']
            else:
                team_text = (self.teamdir / args['teamfile']).text()
            showdown = Showdown(
                team_text,
                PessimisticMinimaxAgent(2, self.pokedata),
                args['username'],
                self.pokedata,
                browser=args['browser'],
                password=args['password'],
            )
            id = self.run_showdown(showdown, args)
            response = {'id': id}
            return jsonify(**response)

    def start_server(self):
        port = 5000
        url = "http://127.0.0.1:{0}".format(port)
        host = '0.0.0.0'
        chromepath = '/usr/bin/google-chrome %s'
        Timer(1.25, lambda: webbrowser.get(chromepath).open(url)).start()
        self.app.run(debug=True, host=host, port=port, use_reloader=False)

    def add_id(self, showdown):
        self.counter += 1
        self.ids[self.counter] = showdown
        return self.counter

    def run_showdown(self, showdown, args):
        Thread(target=showdown.run, args=(args['iterations'],),
                kwargs={
                    'challenge': args['challenge']
                }).start()
        return self.add_id(showdown)

    def get_team_files(self):
        files = self.teamdir.files()
        files = [file.name for file in files]
        return files

def main():
    argparse = ArgumentParser()
    argparse.add_argument("--teamdir", default='teams')
    argparse.add_argument("--datadir", default='data')
    arguments = argparse.parse_args()
    teamdir = arguments.teamdir
    datadir = arguments.datadir
    server = Server(
        teamdir,
        datadir,
    )
    server.start_server()
