import pytest

from casper.protocol import Protocol
from casper.blockchain.blockchain_protocol import BlockchainProtocol
from casper.binary.binary_protocol import BinaryProtocol


@pytest.mark.parametrize(
    'protocol',
    (
        Protocol,
        BlockchainProtocol,
        BinaryProtocol,
    )
)
def test_class_properties_defined(protocol):
    protocol.View
    protocol.Message
    protocol.PlotTool
