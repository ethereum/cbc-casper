from casper.blockchain.blockchain_view import BlockchainView
from casper.blockchain.block import Block
from casper.blockchain.blockchain_plot_tool import BlockchainPlotTool
from casper.protocol import Protocol

class BlockchainProtocol(Protocol):
    View = BlockchainView
    Message = Block
    PlotTool = BlockchainPlotTool
