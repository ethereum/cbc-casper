import pytest
import json

from simulations.json_generator import (
    make_base_exe_obj,
    generate_blockchain_json,
    generate_binary_json,
    generate_integer_json,
    generate_order_json,
    generate_concurrent_json,
    generate_sharding_json
)


@pytest.mark.parametrize(
    'protocol, validators, weights, exe_str, msg_mode, network, rounds',
    [
        ('blockchain', 5, [1, 2, 3, 4, 5], '', 'full', 'no-delay', 5),
        ('binary', 5, [3, 4, 100, 123], '', 'rand', 'step-delay', 5),
    ]
)
def test_make_base_obj(protocol, validators, weights, exe_str, msg_mode, network, rounds):
    base_obj = make_base_exe_obj(protocol, validators, weights, exe_str, msg_mode, network, rounds)

    assert base_obj['protocol'] == protocol
    assert set(base_obj['config']['validators']) == set(weights)
    assert base_obj['execution']['execution_string'] == exe_str


@pytest.mark.parametrize(
    'protocol, validators, weights, exe_str, msg_mode, network, rounds',
    [
        ('blockchain', 5, [1, 2, 3, 4, 5], None, 'random', 'no-delay', 5),
        ('binary', 5, [3, 4, 100, 123], None, 'rand', 'no-network', 5),
    ]
)
def test_make_base_obj_fails_invalid(protocol, validators, weights, exe_str, msg_mode, network, rounds):
    with pytest.raises(KeyError):
        make_base_exe_obj(protocol, validators, weights, exe_str, msg_mode, network, rounds)



@pytest.mark.parametrize(
    'json_generator, protocol, extra_config_fields',
    [
        (generate_binary_json, 'binary', ['initial_estimates']),
        (generate_integer_json, 'integer', ['initial_estimates']),
        (generate_blockchain_json, 'blockchain', []),
        (generate_order_json, 'order', ['initial_estimates']),
        (generate_concurrent_json, 'concurrent', ['starting_outputs', 'genesis_estimate', 'select_outputs', 'create_outputs']),
        (generate_sharding_json, 'sharding', ['num_shards', 'val_select_shards']),
    ]
)
def test_generate_with_correct_fields(json_generator, protocol, extra_config_fields):
    parsed_json = json.loads(json_generator())

    assert parsed_json['protocol'] == protocol

    for field in extra_config_fields:
        # check the existance of the key
        parsed_json['config'][field]
