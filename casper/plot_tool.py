"""The plot tool module ... """

from math import pi
import os
import matplotlib as mpl
import imageio as io
from PIL import Image
import networkx as nx

mpl.use('TkAgg')
import matplotlib.pyplot as plt  # noqa
import pylab  # noqa


BASE = 10000000
IMAGE_LIMIT = 75
FRAMES = "graphs/"
THUMBNAILS = "thumbs/"
COLOURS = ["LightYellow", "Yellow", "Orange", "OrangeRed", "Red", "DarkRed", "Black"]


def plot_view(view, validator_set, colored_bets=None, color_mag=None, edges=None):
    """Creates and displays view graphs."""

    if colored_bets is None:
        colored_bets = set()
    if color_mag is None:
        color_mag = {}
    if edges is None:
        edges = []

    graph = nx.Graph()

    nodes = view.messages

    fig_size = plt.rcParams["figure.figsize"]
    fig_size[0] = 20
    fig_size[1] = 20
    plt.rcParams["figure.figsize"] = fig_size

    for bets in nodes:
        graph.add_edges_from([(bets, bets)])

    edge = []
    if edges == []:
        for bets in nodes:
            for bets2 in bets.justification.latest_messages.values():
                if bets2 is not None:
                    edge.append((bets2, bets))

        edges = [{'edges': edge, 'width': 3, 'edge_color': 'black', 'style': 'solid'}]

    positions = dict()

    sorted_validators = validator_set.sorted_by_name()
    for bets in nodes:
        # Index of val in list may have some small performance concerns.
        positions[bets] = (float)(sorted_validators.index(bets.sender)
                                  + 1)/(float)(len(validator_set) + 1), 0.2 + 0.1*bets.display_height

    node_color_map = {}
    for bets in nodes:
        if bets in colored_bets:
            mag = color_mag[bets]
            node_color_map[bets] = COLOURS[int(len(COLOURS) * mag / len(validator_set))]
            if mag == len(validator_set) - 1:
                node_color_map[bets] = "Black"

        else:
            node_color_map[bets] = 'white'

    color_values = [node_color_map.get(node) for node in nodes]

    labels = {}

    node_sizes = []
    for bets in nodes:
        node_sizes.append(350*pow(bets.sender.weight/pi, 0.5))
        labels[bets] = bets.sequence_number

    nx.draw_networkx_nodes(graph, positions, alpha=0.1, node_color=color_values, nodelist=nodes,
                           node_size=node_sizes, edge_color='black')

    for edge in edges:
        if isinstance(edge, dict):
            nx.draw_networkx_edges(graph, positions, edgelist=(edge['edges']), width=edge['width'],
                                   edge_color=edge['edge_color'], style=edge['style'], alpha=0.5)
        else:
            assert False, edge
    nx.draw_networkx_labels(graph, positions, labels=labels)

    ax = plt.gca()
    ax.collections[0].set_edgecolor("black")
    ax.text(-0.05, 0.1, "Weights: ", fontsize=20)

    for validator in validator_set:
        xpos = (float)(validator.name + 1)/(float)(len(validator_set) + 1) - 0.01
        ax.text(xpos, 0.1, (str)((int)(validator.weight)), fontsize=20)

    pylab.show()
    # pylab.savefig(FRAMES + "graph" + str(BASE + len(nodes)) + ".png")
    # plt.close('all')


def make_thumbnails(frame_count_limit=IMAGE_LIMIT, xsize=1000, ysize=1000):
    """Make thumbnail images in PNG format."""
    file_names = sorted([fn for fn in os.listdir(FRAMES) if fn.endswith('.png')])

    images = []
    for file_name in file_names:
        images.append(Image.open(FRAMES+file_name))
        if len(images) == frame_count_limit:
            break

    size = (xsize, ysize)
    iterator = 0
    for image in images:
        image.thumbnail(size, Image.ANTIALIAS)
        image.save("thumbs/" + str(BASE + iterator) + "thumbnail.png", "PNG")
        iterator += 1
        if iterator == frame_count_limit:
            break


def make_gif(frame_count_limit=IMAGE_LIMIT, destination_filename="mygif.gif", frame_duration=0.2):
    """Make a GIF visualization of view graph."""

    file_names = sorted([file_name for file_name in os.listdir(THUMBNAILS)
                         if file_name.endswith('thumbnail.png')])

    images = []
    for file_name in file_names:
        images.append(Image.open(THUMBNAILS + file_name))
        if len(images) == frame_count_limit:
            break

    iterator = 0
    with io.get_writer(destination_filename, mode='I', duration=frame_duration) as writer:
        for file_name in file_names:
            image = io.imread(THUMBNAILS + file_name)
            writer.append_data(image)
            iterator += 1
            if iterator == frame_count_limit:
                break

    writer.close()
