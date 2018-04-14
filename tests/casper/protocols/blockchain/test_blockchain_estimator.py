'''The forkchoice testing module ... '''
import pytest
import random as r

import casper.protocols.blockchain.forkchoice as forkchoice

from simulations.exe_str_generator import generate_rrob_execution


def test_single_validator_correct_forkchoice(blockchain_instantiated):
    execution_string = 'M-0-A M-0-B M-0-C M-0-D M-0-E M-0-F M-0-G M-0-H'
    blockchain_instantiated.execute(execution_string)

    estimate = blockchain_instantiated.global_validator_set.get_validator_by_name(0).estimate()
    assert estimate == blockchain_instantiated.messages['H']


def test_two_validators_round_robin_forkchoice(blockchain_instantiated):
    execution_string = 'M-0-A SJ-1-A M-1-B SJ-0-B M-0-C SJ-1-C M-1-D SJ-0-D'
    blockchain_instantiated.execute(execution_string)

    estimate_0 = blockchain_instantiated.global_validator_set.get_validator_by_name(0).estimate()
    estimate_1 = blockchain_instantiated.global_validator_set.get_validator_by_name(0).estimate()
    assert estimate_0 == blockchain_instantiated.messages['D']
    assert estimate_1 == blockchain_instantiated.messages['D']


def test_many_val_round_robin_forkchoice(blockchain_instantiated, no_delay):
    execution_string, _ = generate_rrob_execution(5, 10, no_delay)
    print(execution_string)
    blockchain_instantiated.execute(execution_string)
    blockchain_instantiated.execute('M-0-A SJ-1-A SJ-2-A SJ-3-A SJ-4-A')

    for validator in blockchain_instantiated.global_validator_set:
        assert validator.estimate() == blockchain_instantiated.messages['A']


def test_fail_on_tie(blockchain_creator):
    protocol = blockchain_creator([5, 6, 5])
    with pytest.raises(AssertionError):
        protocol.execute('M-1-A SJ-0-A M-0-B SJ-1-B SJ-2-A M-2-C SJ-1-C')
        protocol.global_validator_set.get_validator_by_name(1).estimate()


def test_ignore_zero_weight_validator(blockchain_creator):
    protocol = blockchain_creator([5, 0])
    protocol.execute('M-0-A SJ-1-A M-1-B SJ-0-B')

    for validator in protocol.global_validator_set.get_validators_by_names([0, 1]):
        assert validator.estimate() == protocol.messages['A']


def test_ignore_zero_weight_block(blockchain_creator):
    # for more info about test, see
    # https://gist.github.com/naterush/8d8f6ec3509f50939d7911d608f912f4
    execution_string = (
        'M-0-A1 M-0-A2 M-1-B1 M-1-B2 SJ-3-B2 M-3-D1 '
        'SJ-3-A2 M-3-D2 SJ-2-B1 M-2-C1 SJ-1-D1 '
        'SJ-1-D2 SJ-1-C1'
    )
    protocol = blockchain_creator([10, 9, 8, .5])
    protocol.execute(execution_string)

    validator = protocol.global_validator_set.get_validator_by_name(1)
    assert validator.estimate() == protocol.messages['B2']


def test_reverse_message_arrival_order_forkchoice(blockchain_creator):
    execution_string = (
        'M-0-A SJ-1-A M-1-B SJ-0-B M-0-C SJ-1-C M-1-D SJ-0-D M-1-E SJ-0-E '
        'SJ-2-E SJ-3-A SJ-3-B SJ-3-C SJ-3-D SJ-3-E'
    )
    protocol = blockchain_creator([5, 6, 7, 8.1])
    protocol.execute(execution_string)

    validator = protocol.global_validator_set.get_validator_by_name(3)
    assert validator.estimate() == protocol.messages['E']


@pytest.mark.parametrize(
    'weights, expected',
    [
        ({i: i for i in range(10)}, {9}),
        ({i: 9 - i for i in range(10)}, {0}),
        ({i: i % 5 for i in range(10)}, {4, 9}),
        ({i: 10 for i in range(10)}, {i for i in range(10)}),
        ({}, ValueError),
        ({i: 0 for i in range(10)}, AssertionError),
    ]
)
def test_max_weight_indexes(weights, expected):
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected):
            forkchoice.get_max_weight_indexes(weights)
        return

    assert forkchoice.get_max_weight_indexes(weights) == expected
