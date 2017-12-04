"""The validator testing module ... """

import pytest

from casper.protocols.blockchain.block import Block
from casper.validator import Validator
from casper.protocols.blockchain.blockchain_protocol import BlockchainProtocol
from casper.protocols.binary.binary_protocol import BinaryProtocol



@pytest.mark.parametrize(
    'name, weight, error',
    [
        (1, 10.2, None),
        ("Jim", 5, None),
        (2, 0, None),
        (3, -12, ValueError),
        (None, 13, ValueError),
        (10, None, ValueError),
        (10, 'weightstring', ValueError),
    ]
)
def test_new_validator(name, weight, error):
    if isinstance(error, type) and issubclass(error, Exception):
        with pytest.raises(error):
            Validator(name, weight)
        return

    validator = Validator(name, weight)
    assert validator.name == name
    assert validator.weight == weight


def test_validator_created_with_genesis():
    validator = Validator(0, 1, BlockchainProtocol)
    assert validator.view.last_finalized_block is not None

    validator = Validator(0, 1, BinaryProtocol)
    assert validator.my_latest_message() is not None
