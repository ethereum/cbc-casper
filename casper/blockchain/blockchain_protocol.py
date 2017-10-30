from casper.blockchain.blockchain_view import BlockchainView
from casper.blockchain.block import Block
from casper.blockchain.blockchain_plot_tool import BlockchainPlotTool


class BlockchainProtocol:
    View = BlockchainView
    Message = Block
    PlotTool = BlockchainPlotTool
