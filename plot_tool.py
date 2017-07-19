import networkx as nx
from block import Block
from settings import WEIGHTS, NUM_VALIDATORS, ESTIMATE_SPACE
from math import pi
import matplotlib.pyplot as plt
import pylab
import plot_tool


def dependency_from_same_validator_from_bet(b):
    dependencies = set()

    def recurr(B):
        print b.sender not in B.justification.latest_messages
        if b.sender not in B.justification.latest_messages or B.sequence_number == 1:
            return
        else:
            recurr(B.justification.latest_messages[b.sender])

    recurr(b)

    return dependencies


def dependency_from_same_validator(view):
    dependencies = set()
    for bet in view.messages:
        dependencies = dependencies.union(dependency_from_same_validator_from_bet(bet))

    return dependencies


def get_extension_from_same_validator(view):
    return (dependency_from_same_validator(view)).union(view.messages)


def plot_view(view, coloured_bets, colour='green', use_edges=[]):

    G = nx.DiGraph()

    nodes = get_extension_from_same_validator(view)

    for b in nodes:
        G.add_edges_from([(b, b)])

    if use_edges == []:
        for b in nodes:
            for b2 in b.justification.latest_messages.values():
                G.add_edges_from([(b2, b)])
    else:
        for e in use_edges:
            G.add_edges_from([(e[0], e[1])])

    # G.add_edges_from([('A', 'B'),('C','D'),('G','D')])
    # G.add_edges_from([('C','F')])

    positions = dict()

    for b in nodes:
        positions[b] = (float)(b.sender + 1)/(float)(NUM_VALIDATORS + 1), 0.2 + 0.1*b.height

    node_color_map = {}
    for b in nodes:
        if b in coloured_bets:
            node_color_map[b] = colour
        else:
            node_color_map[b] = 'white'

    color_values = [node_color_map.get(node) for node in G.nodes()]

    labels = {}
    for b in nodes:
        labels[b] = b.estimate
    # labels['B']=r'$b$'

    node_sizes = [700*pow(WEIGHTS[node.sender]/pi, 0.5) for node in G.nodes()]

    nx.draw_networkx_labels(G, positions, labels, font_size=20)

    nx.draw(G, positions, node_color=color_values, node_size=node_sizes, edge_color='black', edge_cmap=plt.cm.Reds)

    ax = plt.gca()  # to get the current axis
    ax.collections[0].set_edgecolor("black")

    ax.text(-0.05, 0.1, "Weights: ", fontsize=20)

    for v in xrange(NUM_VALIDATORS):
        xpos = (float)(v + 1)/(float)(NUM_VALIDATORS + 1) - 0.01
        ax.text(xpos, 0.1, (str)((int)(WEIGHTS[v])), fontsize=20)

    pylab.show()
