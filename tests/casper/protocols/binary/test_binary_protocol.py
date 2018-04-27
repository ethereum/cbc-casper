"""The language testing module ... """
import pytest
import json

from casper.protocols.binary.binary_protocol import BinaryProtocol

from simulations.json_generator import generate_binary_json, generate_blockchain_json


@pytest.mark.parametrize(
    'initial_estimates',
    [
        ([1, 0, 1, 0, 1]),
        ([0, 0, 0, 0, 0]),
        ([1, 1, 1, 1, 1]),
    ]
)
def test_saves_initial_estimates(initial_estimates):
    exe_obj = generate_binary_json(init_est=initial_estimates)
    parsed_json = json.loads(exe_obj)

    for i, estimate in enumerate(parsed_json['config']['initial_estimates']):
        assert estimate == initial_estimates[i]

    protocol = BinaryProtocol(exe_obj, False, False, 1)

    for validator in protocol.global_validator_set:
        assert len(validator.view.justified_messages) == 1
        assert validator.estimate() == initial_estimates[validator.name]


@pytest.mark.parametrize(
    'invalid_json',
    [
        generate_binary_json(init_est=[2, 2, 2, 2, 2]),
        generate_binary_json(init_est=[1]),
        generate_blockchain_json(),
    ]
)
def test_only_parses_valid_json(invalid_json):
    with pytest.raises(AssertionError):
        BinaryProtocol.parse_json(invalid_json)
