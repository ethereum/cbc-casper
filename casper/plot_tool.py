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
IMAGE_LIMIT = 500
FRAMES = "graphs/"
THUMBNAILS = "thumbs/"
COLOURS = ["LightYellow", "Yellow", "Orange", "OrangeRed", "Red", "DarkRed", "Black"]


class PlotTool(object):

    def __init__(self, display, save, node_shape):
        self.display = display
        self.save = save
        self.node_shape = node_shape

        if save:
            self._create_graph_folder()

        self.report_number = 0


    def _create_graph_folder(self):
        graph_path = os.path.dirname(os.path.abspath(__file__)) + '/../graphs/'
        # if there isn't a graph folder, make one!
        if not os.path.isdir(graph_path):
            os.makedirs(graph_path)

        # find the next name for the next plot!
        graph_num = 0
        while True:
            new_plot = graph_path + 'graph_num_' + str(graph_num)
            graph_num += 1
            if not os.path.isdir(new_plot):
                os.makedirs(new_plot)
                break

        self.graph_path = new_plot + "/"
        self.thumbnail_path = self.graph_path + "thumbnails/"
        os.makedirs(self.thumbnail_path)

    def build_viewgraph(self, view, validator_set, message_colors, message_labels, edges):
        """Creates and displays view graphs."""

        graph = nx.Graph()

        nodes = view.messages

        fig_size = plt.rcParams["figure.figsize"]
        fig_size[0] = 20
        fig_size[1] = 20
        plt.rcParams["figure.figsize"] = fig_size

        for message in nodes:
            graph.add_edges_from([(message, message)])

        edge = []
        if edges == []:
            for message in nodes:
                for msg_in_justification in message.justification.latest_messages.values():
                    if msg_in_justification is not None:
                        edge.append((msg_in_justification, message))

            edges = [{'edges': edge, 'width': 3, 'edge_color': 'black', 'style': 'solid'}]

        positions = dict()

        sorted_validators = validator_set.sorted_by_name()
        for message in nodes:
            # Index of val in list may have some small performance concerns.
            positions[message] = (float)(sorted_validators.index(message.sender) + 1) / \
                                 (float)(len(validator_set) + 1), 0.2 + 0.1*message.display_height

        node_color_map = {}
        for message in nodes:
            if message not in message_colors:
                node_color_map[message] = 'white'
            elif message_colors[message] == len(validator_set) - 1:
                node_color_map[message] = "Black"
            else:
                node_color_map[message] = COLOURS[int(len(COLOURS) * message_colors[message] / \
                                          len(validator_set))]


        color_values = [node_color_map.get(node) for node in nodes]

        labels = {}

        node_sizes = []
        for message in nodes:
            node_sizes.append(350 * pow(message.sender.weight / pi, 0.5))
            labels[message] = message_labels.get(message, '')

        nx.draw_networkx_nodes(graph, positions, alpha=0.5, node_color=color_values, nodelist=nodes,
                               node_size=node_sizes, node_shape=self.node_shape, edge_color='black')

        for edge in edges:
            if isinstance(edge, dict):
                nx.draw_networkx_edges(
                    graph,
                    positions,
                    edgelist=(edge['edges']),
                    width=edge['width'],
                    edge_color=edge['edge_color'],
                    style=edge['style'],
                    alpha=0.5
                )
            else:
                assert False, edge
        nx.draw_networkx_labels(graph, positions, labels=labels)

        ax = plt.gca()
        ax.collections[0].set_edgecolor("black")
        ax.text(-0.05, 0.1, "Weights: ", fontsize=20)

        for validator in validator_set:
            xpos = (float)(validator.name + 1)/(float)(len(validator_set) + 1) - 0.01
            ax.text(xpos, 0.1, (str)((int)(validator.weight)), fontsize=20)


    def next_viewgraph(
            self,
            view,
            validator_set,
            message_colors=None,
            message_labels=None,
            edges=None
    ):
        """Generates the next viewgraph, and saves and/or displays it"""
        if message_colors is None:
            message_colors = {}
        if message_labels is None:
            message_labels = {}
        if edges is None:
            edges = []

        self.report_number += 1

        # TODO: if we save and plot the graph, we currently build it twice
        # issues as pyplot clears the graph otherwise, should try to fix this
        if self.save:
            self.build_viewgraph(
                view,
                validator_set,
                message_colors=message_colors,
                message_labels=message_labels,
                edges=edges
            )

            plt.savefig(self.graph_path + '/' + str(1000 + self.report_number) + ".png")
            plt.close('all')

        if self.display:
            self.build_viewgraph(
                view,
                validator_set,
                message_colors=message_colors,
                message_labels=message_labels,
                edges=edges
            )

            plt.show()

    def make_thumbnails(self, frame_count_limit=IMAGE_LIMIT, xsize=1000, ysize=1000):
        """Make thumbnail images in PNG format."""

        file_names = sorted([fn for fn in os.listdir(self.graph_path) if fn.endswith('.png')])

        if len(file_names) >= frame_count_limit:
            raise Exception("To many frames!")

        images = []
        for file_name in file_names:
            images.append(Image.open(self.graph_path + file_name))


        size = (xsize, ysize)
        iterator = 0
        for image in images:
            image.thumbnail(size, Image.ANTIALIAS)
            image.save(self.thumbnail_path + str(1000 + iterator) + "thumbnail.png", "PNG")
            iterator += 1


    def make_gif(self, frame_count_limit=IMAGE_LIMIT, gif_name="mygif.gif", frame_duration=0.4):
        """Make a GIF visualization of view graph."""

        self.make_thumbnails(frame_count_limit=frame_count_limit)

        file_names = sorted([file_name for file_name in os.listdir(self.thumbnail_path)
                             if file_name.endswith('thumbnail.png')])

        images = []
        for file_name in file_names:
            images.append(Image.open(self.thumbnail_path + file_name))

        destination_filename = self.graph_path + gif_name

        iterator = 0
        with io.get_writer(destination_filename, mode='I', duration=frame_duration) as writer:
            for file_name in file_names:
                image = io.imread(self.thumbnail_path + file_name)
                writer.append_data(image)
                iterator += 1

        writer.close()
