import random as r

from casper.protocols.concurrent.concurrent_view import ConcurrentView
from casper.protocols.concurrent.block import Block
from casper.protocols.concurrent.concurrent_plot_tool import ConcurrentPlotTool

from casper.protocol import Protocol


class ConcurrentProtocol(Protocol):
    View = ConcurrentView
    Message = Block
    PlotTool = ConcurrentPlotTool

    genesis_block = None

    @classmethod
    def initial_message(cls, validator):
        if not cls.genesis_block:
            blocks = set([None])
            inputs = set([r.randint(0, 1000000000) for x in range(7)])
            outputs = set([r.randint(0, 1000000000) for x in inputs])

            estimate = {'blocks': blocks, 'inputs': inputs, 'outputs': outputs}
            cls.genesis_block = Block(estimate, dict(), validator, -1, 0)
        return cls.genesis_block
