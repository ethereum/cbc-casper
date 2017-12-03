from casper.protocols.order.order_view import OrderView
from casper.protocols.order.bet import Bet
from casper.protocols.order.order_plot_tool import OrderPlotTool
from casper.protocol import Protocol


class OrderProtocol(Protocol):
    View = OrderView
    Message = Bet
    PlotTool = OrderPlotTool
