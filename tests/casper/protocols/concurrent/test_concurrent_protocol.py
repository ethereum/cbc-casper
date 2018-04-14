"""The language testing module ... """
import pytest
from random import choice

from casper.protocols.concurrent.concurrent_protocol import ConcurrentProtocol
from simulations.json_generator import generate_binary_json, generate_concurrent_json


def test_sends_validators_genesis(concurrent_instantiated):
    assert len(concurrent_instantiated.global_view.justified_messages) == 1
    justified = {m for m in concurrent_instantiated.global_view.justified_messages.values()}
    genesis = justified.pop()

    for validator in concurrent_instantiated.global_validator_set:
        justified = validator.view.justified_messages.values()
        assert genesis in justified
        assert len(justified) == 1


@pytest.mark.parametrize(
    'invalid_json',
    [
        generate_binary_json(),
    ]
)
def test_only_parses_valid_json(invalid_json):
    with pytest.raises(AssertionError):
        ConcurrentProtocol.parse_json(invalid_json)
