import json
from random import (
    randint,
    sample
)

from simulations.network_delay import (
    SELECT_NETWORK_DELAY
)
from simulations.exe_str_generator import (
    SELECT_EXECUTION_GENERATOR
)
from simulations.utils import (
    generate_random_gaussian_weights,
)

LIST = ["dog", "frog", "horse", "pig", "rat", "whale", "cat"]

def make_base_exe_obj(
        protocol,
        validators,
        weights,
        exe_str,
        msg_mode,
        network,
        rounds
    ):
    """Creates a dictonary with all shared fields between protocols"""
    data = {}
    data['config'] = {}
    data['execution'] = {}

    data['protocol'] = protocol

    val_weights = weights if weights else generate_random_gaussian_weights(validators)
    data['config']['validators'] = val_weights

    if exe_str:
        data['execution']['msg_per_round'] = 1
        data['execution']['execution_string'] = exe_str
        return data

    execution_string_generator = SELECT_EXECUTION_GENERATOR[msg_mode]
    network_delay_function = SELECT_NETWORK_DELAY[network]

    execution_string, msg_per_round = execution_string_generator(
        validators, rounds, network_delay_function
    )
    data['execution']['msg_per_round'] = msg_per_round
    data['execution']['execution_string'] = execution_string

    return data


def generate_binary_json(
        validators=5,
        weights=None,
        exe_str=None,
        msg_mode='rand',
        network='no-delay',
        rounds=10,
        init_est=None
    ):
    """Generates JSON string for binary protocol execution"""
    exe_obj = make_base_exe_obj(
        'binary',
        validators,
        weights,
        exe_str,
        msg_mode,
        network,
        rounds
    )

    initial_estimates = init_est if init_est else [randint(0, 1) for _ in range(validators)]
    exe_obj['config']['initial_estimates'] = initial_estimates

    return json.dumps(exe_obj)


def generate_integer_json(
        validators=5,
        weights=None,
        exe_str=None,
        msg_mode='rand',
        network='no-delay',
        rounds=10,
        init_est=None,
        max_int=100
    ):
    """Generates JSON string for integer protocol execution"""
    exe_obj = make_base_exe_obj(
        'integer',
        validators,
        weights,
        exe_str,
        msg_mode,
        network,
        rounds
    )

    initial_estimates = init_est if init_est else [randint(0, max_int) for _ in range(validators)]
    exe_obj['config']['initial_estimates'] = initial_estimates

    return json.dumps(exe_obj)


def generate_blockchain_json(
        validators=5,
        weights=None,
        exe_str=None,
        msg_mode='rand',
        network='no-delay',
        rounds=10,
    ):
    """Generates JSON string for blockchain protocol execution"""
    exe_obj = make_base_exe_obj(
        'blockchain',
        validators,
        weights,
        exe_str,
        msg_mode,
        network,
        rounds
    )
    return json.dumps(exe_obj)


def generate_order_json(
        validators=5,
        weights=None,
        exe_str=None,
        msg_mode='rand',
        network='no-delay',
        rounds=10,
        init_est=None
    ):
    """Generates JSON string for order protocol execution"""
    exe_obj = make_base_exe_obj(
        'order',
        validators,
        weights,
        exe_str,
        msg_mode,
        network,
        rounds
    )

    if init_est:
        initial_estimates = init_est
    else:
        initial_estimates = [sample(LIST, len(LIST)) for _ in range(validators)]

    exe_obj['config']['initial_estimates'] = initial_estimates

    return json.dumps(exe_obj)


def generate_sharding_json(
        validators=5,
        weights=None,
        exe_str=None,
        msg_mode='rand',
        network='no-delay',
        rounds=10,
        num_shards=2,
        select_shards=None
    ):
    """Generates JSON string for sharded-blockchain protocol execution"""
    exe_obj = make_base_exe_obj(
        'sharding',
        validators,
        weights,
        exe_str,
        msg_mode,
        network,
        rounds
    )

    exe_obj['config']['num_shards'] = num_shards

    if select_shards:
        val_select_shards = select_shards
    else:
        val_select_shards = ["random" for _ in range(validators)]

    exe_obj['config']['val_select_shards'] = val_select_shards

    return json.dumps(exe_obj)


def generate_concurrent_json(
        validators=5,
        weights=None,
        exe_str=None,
        msg_mode='rand',
        network='no-delay',
        rounds=10,
        start_out=None,
        gen_est=None,
        select_outputs='random',
        create_outputs='random',
    ):
    """Generates JSON string for concurrent schedule protocol execution"""
    exe_obj = make_base_exe_obj(
        'concurrent',
        validators,
        weights,
        exe_str,
        msg_mode,
        network,
        rounds
    )

    if start_out:
        starting_outputs = start_out
    else:
        starting_outputs = [randint(0, 100000) for _ in range(10)]

    exe_obj['config']['starting_outputs'] = starting_outputs

    if gen_est:
        genesis_estimate = gen_est
    else:
        genesis_estimate = sample(starting_outputs, round(len(starting_outputs) / 2))

    exe_obj['config']['genesis_estimate'] = genesis_estimate

    exe_obj['config']['select_outputs'] = select_outputs
    exe_obj['config']['create_outputs'] = create_outputs

    return json.dumps(exe_obj)

SELECT_JSON_GENERATOR = {
    'blockchain': generate_blockchain_json,
    'binary': generate_binary_json,
    'integer': generate_integer_json,
    'order': generate_order_json,
    'concurrent': generate_concurrent_json,
    'sharding': generate_sharding_json
}
