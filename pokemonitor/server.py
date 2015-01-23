from pokemonitor import app

def start(port=8080, host='0.0.0.0'):
    app.debug = True
    app.run(port=port, host=host)
