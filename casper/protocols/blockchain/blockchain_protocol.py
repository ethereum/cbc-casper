from casper.protocols.blockchain.blockchain_view import BlockchainView
from casper.protocols.blockchain.block import Block
from casper.protocols.blockchain.blockchain_plot_tool import BlockchainPlotTool
from casper.protocol import Protocol


class BlockchainProtocol(Protocol):
    View = BlockchainView
    Message = Block
    PlotTool = BlockchainPlotTool

    genesis_block = None

    @classmethod
    def initial_message(cls, validator):
        if not cls.genesis_block:
            cls.genesis_block = Block(None, dict(), validator, -1, 0)
        return cls.genesis_block
