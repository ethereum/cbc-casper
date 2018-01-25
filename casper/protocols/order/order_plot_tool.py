"""The order plot tool implements functions for plotting order consensus
NOTE: currently only prints to terminal instead of plotting
"""

from casper.plot_tool import PlotTool


class OrderPlotTool(PlotTool):
    """The module contains functions for plotting an order data structure"""

    def __init__(self, display, save, view, validator_set):
        self.view = view

        print("initial validator bets:")
        for validator in validator_set.sorted_by_name():
            print("{} [{}]:\t{}".format(validator.name, round(validator.weight, 2), validator.estimate()))
        print()

    def update(self, message_paths=None, sent_messages=None, new_messages=None):
        if message_paths is None:
            message_paths = []
        if sent_messages is None:
            sent_messages = dict()
        if new_messages is None:
            new_messages = dict()

    def plot(self):
        print("{}:\t{}".format(round(self.view.last_fault_tolerance, 1), self.view.estimate()))

    def next_viewgraph(
            self,
            view,
            validator_set,
            message_colors=None,
            message_labels=None,
            edges=None
    ):
        pass

    def build_viewgraph(self, view, validator_set, message_colors, message_labels, edges):
        pass

    def make_thumbnails(self, frame_count_limit=None, xsize=None, ysize=None):
        pass

    def make_gif(self, frame_count_limit=None, gif_name=None, frame_duration=None):
        pass
