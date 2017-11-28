from casper.protocols.integer.integer_view import IntegerView
from casper.protocols.integer.bet import Bet
from casper.protocols.integer.integer_plot_tool import IntegerPlotTool
from casper.protocol import Protocol


class IntegerProtocol(Protocol):
    View = IntegerView
    Message = Bet
    PlotTool = IntegerPlotTool
