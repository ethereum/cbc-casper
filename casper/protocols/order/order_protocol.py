import random as r
import copy

from casper.protocols.order.order_view import OrderView
from casper.protocols.order.bet import Bet
from casper.protocols.order.order_plot_tool import OrderPlotTool
from casper.protocol import Protocol


class OrderProtocol(Protocol):
    View = OrderView
    Message = Bet
    PlotTool = OrderPlotTool

    LIST = ["dog", "frog", "horse", "pig", "rat", "whale", "cat"]

    @staticmethod
    def initial_message(validator):
        if not validator:
            return None

        rand_order_list = copy.deepcopy(OrderProtocol.LIST)
        r.shuffle(rand_order_list)

        return Bet(
            rand_order_list,
            dict(),
            validator,
            0,
            0
        )
