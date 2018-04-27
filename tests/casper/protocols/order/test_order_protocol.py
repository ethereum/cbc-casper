"""The language testing module ... """
import pytest
import json

from casper.protocols.order.order_protocol import OrderProtocol
from simulations.json_generator import generate_order_json, generate_blockchain_json

@pytest.mark.parametrize(
    'initial_estimates',
    [
        ([['A'], ['A'], ['A'], ['A'], ['A']]),
        ([['A', 'B'], ['A', 'B'], ['B', 'A'], ['B', 'A'], ['B', 'A']]),
    ]
)
def test_saves_initial_estimates(initial_estimates):
    exe_obj = generate_order_json(init_est=initial_estimates)
    parsed_json = json.loads(exe_obj)

    for i, estimate in enumerate(parsed_json['config']['initial_estimates']):
        assert estimate == initial_estimates[i]

    protocol = OrderProtocol(exe_obj, False, False, 1)

    for validator in protocol.global_validator_set:
        assert len(validator.view.justified_messages) == 1
        assert validator.estimate() == initial_estimates[validator.name]


@pytest.mark.parametrize(
    'invalid_json',
    [
        generate_order_json(init_est=['Hi', [], [], [], []]),
        generate_order_json(init_est=[None]),
        generate_blockchain_json(),
    ]
)
def test_only_parses_valid_json(invalid_json):
    print(invalid_json)
    with pytest.raises(Exception):
        OrderProtocol.parse_json(invalid_json)
