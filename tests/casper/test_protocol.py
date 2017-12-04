import pytest

from casper.protocol import Protocol
from casper.protocols.blockchain.blockchain_protocol import BlockchainProtocol
from casper.protocols.binary.binary_protocol import BinaryProtocol
from casper.protocols.integer.integer_protocol import IntegerProtocol
from casper.protocols.order.order_protocol import OrderProtocol


@pytest.mark.parametrize(
    'protocol',
    (
        Protocol,
        BlockchainProtocol,
        BinaryProtocol,
        IntegerProtocol
    )
)
def test_class_properties_defined(protocol):
    protocol.View
    protocol.Message
    protocol.PlotTool
