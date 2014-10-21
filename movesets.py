from bs4 import BeautifulSoup
import requests
import json
url = "http://www.smogon.com/dex/api/query"

fields = {"tag":{"gen":"xy","alias":"ou"},"$":["name","alias","gen","description",{"genfamily":["alias","gen"]},{"pokemonalts":["name","alias","base_alias","gen",{"types":["alias","name","gen"]},{"abilities":["alias","name","gen"]},{"tags":["name","alias","shorthand","gen"]},"weight","height","hp","patk","pdef","spatk","spdef","spe"]}]}

params = {"q": json.dumps(fields)}

results = requests.get(url, params=params)
results = results.json()
if 'result' not in results:
    print results
else:
    for result in results["result"]:
        for alts in result['pokemonalts']:
            print "Pokemon:", alts["name"]
