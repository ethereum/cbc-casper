from casper.protocols.blockchain.blockchain_view import BlockchainView
from casper.protocols.blockchain.block import Block
from casper.protocols.blockchain.blockchain_plot_tool import BlockchainPlotTool
from casper.protocol import Protocol


class BlockchainProtocol(Protocol):
    View = BlockchainView
    Message = Block
    PlotTool = BlockchainPlotTool
