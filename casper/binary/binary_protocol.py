from casper.binary.binary_view import BinaryView
from casper.binary.bet import Bet
from casper.binary.binary_plot_tool import BinaryPlotTool
from casper.protocol import Protocol


class BinaryProtocol(Protocol):
    View = BinaryView
    Message = Bet
    PlotTool = BinaryPlotTool
