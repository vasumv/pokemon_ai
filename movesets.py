import requests
import json
url = "http://www.smogon.com/dex/api/query"

fields = ["name", "alias", {"movesets":["name",
                                        {"items":["alias","name"]},
                                        {"abilities":["alias","name","gen"]},
                                        {"evconfigs":["hp","patk","pdef","spatk","spdef","spe"]},
                                        {"natures":["hp","patk","pdef","spatk","spdef","spe"]}]}]

query = {"pokemon":{"gen":"xy","alias":"abomasnow"}, "$": fields}
params = {"q": json.dumps(query)}

results = requests.get(url, params=params).json()
if 'result' in results:
    print results['result']
else:
    print results
