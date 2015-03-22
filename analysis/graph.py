import matplotlib.pyplot as plt
import networkx as nx
import json
G = nx.Graph()
with open("../data/graph_poke2.json") as fp:
    data = json.loads(fp.read())['cooccurences']
print (data['Abomasnow'])
for move in data["Abomasnow"]:
    G.add_node(move)
    for othermove in data["Abomasnow"][move]:
        G.add_edge(move, othermove, weight = data["Abomasnow"][move][othermove])

pos = nx.graphviz_layout(G)
edge_weight=dict([((u,v,),int(d['weight'])) for u,v,d in G.edges(data=True)])
nx.draw_networkx_edge_labels(G,pos,edge_labels=edge_weight)
nx.draw_networkx_nodes(G,pos)
nx.draw_networkx_edges(G,pos)
#nx.draw_networkx_labels(G,pos)

plt.axis('off')
plt.savefig('graph.png', dpi=120, transparent=True)
