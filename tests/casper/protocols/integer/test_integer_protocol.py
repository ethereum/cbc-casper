"""The language testing module ... """
import pytest
import json

from casper.protocols.integer.integer_protocol import IntegerProtocol
from simulations.json_generator import generate_integer_json, generate_blockchain_json

@pytest.mark.parametrize(
    'initial_estimates',
    [
        ([100, 50, 1, 0, 24]),
        ([0, 0, 700, 0, 0]),
    ]
)
def test_saves_initial_estimates(initial_estimates):
    exe_obj = generate_integer_json(init_est=initial_estimates)
    parsed_json = json.loads(exe_obj)

    for i, estimate in enumerate(parsed_json['config']['initial_estimates']):
        assert estimate == initial_estimates[i]

    protocol = IntegerProtocol(exe_obj, False, False, 1)

    for validator in protocol.global_validator_set:
        assert len(validator.view.justified_messages) == 1
        assert validator.estimate() == initial_estimates[validator.name]


@pytest.mark.parametrize(
    'invalid_json',
    [
        generate_integer_json(init_est=['Hi', 2, 2, 2, 2]),
        generate_integer_json(init_est=[None]),
        generate_blockchain_json(),
    ]
)
def test_only_parses_valid_json(invalid_json):
    with pytest.raises(AssertionError):
        IntegerProtocol.parse_json(invalid_json)
