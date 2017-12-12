"""The BlockchainView testing module..."""
import pytest

from casper.protocols.blockchain.blockchain_protocol import BlockchainProtocol
from simulations.blockchain_test_lang import BlockchainTestLang


@pytest.mark.skip(reason="test not yet implemented")
def test_add_justified_message():
    pass

@pytest.mark.skip(reason="test not yet implemented")
def test_dont_add_non_justified_message():
    pass

@pytest.mark.skip(reason="test not yet implemented")
def test_resolve_non_justified_message_when_justification_arrives():
    pass
