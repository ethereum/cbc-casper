from casper.integer.integer_view import IntegerView
from casper.integer.bet import Bet
from casper.binary.binary_plot_tool import BinaryPlotTool
from casper.protocol import Protocol


class IntegerProtocol(Protocol):
    View = IntegerView
    Message = Bet
    PlotTool = BinaryPlotTool
