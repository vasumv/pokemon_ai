from flask import Flask
from argparse import ArgumentParser
app = Flask(__name__, static_folder='static')

from server import start
from route import initialize

def main():
    argparser = ArgumentParser()
    argparser.add_argument('-P', '--port', default=8080, type=int)
    argparser.add_argument('-H', '--host', default='0.0.0.0', type=str)

    args = argparser.parse_args()

    initialize()
    start(port=args.port, host=args.host)
