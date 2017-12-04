import random as r

from casper.protocols.binary.binary_view import BinaryView
from casper.protocols.binary.bet import Bet
from casper.protocols.binary.binary_plot_tool import BinaryPlotTool
from casper.protocol import Protocol


class BinaryProtocol(Protocol):
    View = BinaryView
    Message = Bet
    PlotTool = BinaryPlotTool

    @staticmethod
    def initial_message(validator):
        if not validator:
            return None

        rand_int = r.randint(0, 1)

        return Bet(
            rand_int,
            dict(),
            validator,
            0,
            0
        )
