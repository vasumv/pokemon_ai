from flask import request, render_template, jsonify
from pokemonitor import app
from bots import update_status, get_bots

def initialize():

    @app.route('/')
    def index():
        return app.send_static_file('index.html')

    @app.route('/api/update', methods=['GET', 'POST'])
    def update():
        update_status(request.json)
        return jsonify({})

    @app.route('/api/status', methods=['get'])
    def status():
        return jsonify(get_bots())
