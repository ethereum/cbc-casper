"""The plot tool module ... """
from math import pi
import os
import networkx as nx

import matplotlib as mpl
mpl.use('TkAgg')
import matplotlib.pyplot as plt
import pylab
import imageio as io

from PIL import Image

import casper.settings as s


base = 10000000
IMAGE_LIMIT = 75
FRAMES = "graphs/"
THUMBNAILS = "thumbs/"
colors = ["LightYellow", "Yellow", "Orange", "OrangeRed", "Red", "DarkRed", "Black"]


def plot_view(view, validator_set, coloured_bets=[], colour_mag=dict(), edges=[]):
    """Creates and displays view graphs."""
    G = nx.Graph()

    nodes = view.messages

    fig_size = plt.rcParams["figure.figsize"]
    fig_size[0] = 20
    fig_size[1] = 20
    plt.rcParams["figure.figsize"] = fig_size

    for b in nodes:
        G.add_edges_from([(b, b)])

    e = []
    if edges == []:
        for b in nodes:
            for b2 in b.justification.latest_messages.values():
                if b2 is not None:
                    e.append((b2, b))

        edges = [{'edges': e, 'width': 3, 'edge_color': 'black', 'style': 'solid'}]

    positions = dict()

    for b in nodes:
        # assuming validator name here is super hacky
        positions[b] = (float)(b.sender.name + 1)/(float)(len(validator_set) + 1), 0.2 + 0.1*b.height

    node_color_map = {}
    for b in nodes:
        if b in coloured_bets:
            mag = colour_mag[b]
            node_color_map[b] = colors[int(len(colors) * mag / len(validator_set))]
            if mag == len(validator_set) - 1:
                node_color_map[b] = "Black"

        else:
            node_color_map[b] = 'white'

    color_values = [node_color_map.get(node) for node in nodes]

    labels = {}

    node_sizes = []
    for b in nodes:
        node_sizes.append(350*pow(b.sender.weight/pi, 0.5))
        labels[b] = b.sequence_number

    nx.draw_networkx_nodes(G, positions, alpha=0.1, node_color=color_values, nodelist=nodes,
                           node_size=node_sizes, edge_color='black')

    for e in edges:
        if isinstance(e, dict):
            nx.draw_networkx_edges(G, positions, edgelist=(e['edges']), width=e['width'],
                                   edge_color=e['edge_color'], style=e['style'], alpha=0.5)
        else:
            assert False, e
    nx.draw_networkx_labels(G, positions, labels=labels)

    ax = plt.gca()
    ax.collections[0].set_edgecolor("black")
    ax.text(-0.05, 0.1, "Weights: ", fontsize=20)

    for v in validator_set:
        xpos = (float)(v.name + 1)/(float)(len(validator_set) + 1) - 0.01
        ax.text(xpos, 0.1, (str)((int)(v.weight)), fontsize=20)

    pylab.show()
    # pylab.savefig(FRAMES + "graph" + str(base + len(nodes)) + ".png")
    # plt.close('all')


def make_thumbnails(frame_count_limit=IMAGE_LIMIT, xsize=1000, ysize=1000):
    """Make thumbnail images in PNG format."""
    file_names = sorted([fn for fn in os.listdir(FRAMES) if fn.endswith('.png')])

    images = []
    for fn in file_names:
        images.append(Image.open(FRAMES+fn))
        if len(images) == frame_count_limit:
            break

    size = (xsize, ysize)
    iterator = 0
    for im in images:
        im.thumbnail(size, Image.ANTIALIAS)
        im.save("thumbs/" + str(base + iterator) + "thumbnail.png", "PNG")
        iterator += 1
        if iterator == frame_count_limit:
            break


def make_gif(frame_count_limit=IMAGE_LIMIT, destination_filename="mygif.gif", frame_duration=0.2):
    """Make a GIF visualization of view graph."""

    file_names = sorted([fn for fn in os.listdir(THUMBNAILS) if fn.endswith('thumbnail.png')])

    images = []
    for fn in file_names:
        images.append(Image.open(THUMBNAILS + fn))
        if len(images) == frame_count_limit:
            break

    iterator = 0
    with io.get_writer(destination_filename, mode='I', duration=frame_duration) as writer:
        for filename in file_names:
            image = io.imread(THUMBNAILS + filename)
            writer.append_data(image)
            iterator += 1
            if iterator == frame_count_limit:
                break

    writer.close()
