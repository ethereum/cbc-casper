"""The validator testing module ... """
import pytest

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


def test_validator_created_with_genesis(genesis_protocol):
    validator = Validator(0, 1, genesis_protocol)
    assert validator.view.last_finalized_block is not None


def test_validator_created_with_inital_message(rand_start_protocol):
    validator = Validator(0, 1, rand_start_protocol)
    assert validator.my_latest_message() is not None
