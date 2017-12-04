import random as r

from casper.protocols.integer.integer_view import IntegerView
from casper.protocols.integer.bet import Bet
from casper.protocols.integer.integer_plot_tool import IntegerPlotTool
from casper.protocol import Protocol


class IntegerProtocol(Protocol):
    View = IntegerView
    Message = Bet
    PlotTool = IntegerPlotTool

    @staticmethod
    def initial_message(validator):
        if not validator:
            return None

        rand_int = r.randint(0, 100)

        return Bet(
            rand_int,
            dict(),
            validator,
            0,
            0
        )
