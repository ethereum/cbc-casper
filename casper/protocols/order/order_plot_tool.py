"""The order plot tool implements functions for plotting order consensus
NOTE: currently only prints to terminal instead of plotting
"""
from casper.plot_tool import PlotTool


class OrderPlotTool(PlotTool):
    """The module contains functions for plotting an order data structure"""

    def __init__(self, display, save, view, validator_set):
        self.display = display
        self.view = view
        self.round = 0
        self.save = save
        self.display = display

    def update(self, new_messages=None):
        return

    def plot(self):
        for validator in self.view.latest_messages:
            print("{}:\t{}".format(validator.name, validator.estimate()))

        print()
        self.round += 1
