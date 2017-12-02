from casper.protocols.binary.binary_view import BinaryView
from casper.protocols.binary.bet import Bet
from casper.protocols.integer.integer_plot_tool import IntegerPlotTool
from casper.protocol import Protocol


class BinaryProtocol(Protocol):
    View = BinaryView
    Message = Bet
    PlotTool = IntegerPlotTool
