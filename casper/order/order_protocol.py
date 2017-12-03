from casper.order.order_view import OrderView
from casper.order.bet import Bet
from casper.order.order_plot_tool import OrderPlotTool
from casper.protocol import Protocol


class OrderProtocol(Protocol):
    View = OrderView
    Message = Bet
    PlotTool = OrderPlotTool
