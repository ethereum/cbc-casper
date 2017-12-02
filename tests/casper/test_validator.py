"""The validator testing module ... """

import pytest

from casper.protocols.blockchain.block import Block
from casper.justification import Justification
from casper.validator import Validator


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


def test_check_estimate_safety_without_validator_set():
    validator = Validator("cool", 10.2)
    block = Block(None, Justification(), validator)

    with pytest.raises(AttributeError):
        validator.check_estimate_safety(block)
