"""The BlockchainView testing module..."""
import pytest

from casper.blockchain.blockchain_protocol import BlockchainProtocol
from simulations.testing_language import TestLangCBC


@pytest.mark.skip(reason="test not yet implemented")
def test_add_justified_message():
    pass

@pytest.mark.skip(reason="test not yet implemented")
def test_dont_add_non_justified_message():
    pass

@pytest.mark.skip(reason="test not yet implemented")
def test_resolve_non_justified_message_when_justification_arrives():
    pass
