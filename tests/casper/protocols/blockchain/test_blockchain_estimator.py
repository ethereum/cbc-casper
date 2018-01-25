"""The forkchoice testing module ... """
import pytest
import random as r

import casper.protocols.blockchain.forkchoice as forkchoice


def test_single_validator_correct_forkchoice(blockchain_lang_runner):
    """ This tests that a single validator remains on their own chain """
    test_string = ""
    for i in range(100):
        test_string += "M0-" + str(i) + " " + "CE0-" + str(i) + " "
    test_string = test_string[:-1]

    blockchain_lang_runner({0: 10}, test_string)


def test_two_validators_round_robin_forkchoice(blockchain_lang_runner):
    test_string = "M0-A SJ1-A M1-B SJ0-B M0-C SJ1-C M1-D SJ0-D CE0-D P"
    blockchain_lang_runner({0: 10, 1: 11}, test_string)


def test_many_val_round_robin_forkchoice(blockchain_lang_runner):
    """
    Tests that during a perfect round robin,
    validators choose the one chain as their fork choice
    """
    test_string = ""
    for i in range(25):
        test_string += "M" + str(i % 10) + "-" + str(i) + " " \
                     + "SJ" + str((i + 1) % 10) + "-" + str(i) + " " \
                     + "CE" + str((i + 1) % 10) + "-" + str(i) + " "
    test_string = test_string[:-1]

    blockchain_lang_runner(
        {i: 10 - i + r.random() for i in range(10)},
        test_string
    )


def test_fail_on_tie(blockchain_lang_runner):
    """
    Tests that if there are two subsets of the validator
    set with the same weight, the forkchoice fails
    """
    test_string = "M1-A SJ0-A M0-B SJ1-B SJ2-A M2-C SJ1-C CE1-C"
    with pytest.raises(AssertionError):
        blockchain_lang_runner({0: 5, 1: 6, 2: 5}, test_string)


def test_ignore_zero_weight_validator(blockchain_lang_runner):
    """
    Tests that a validator with zero weight
    will not affect the forkchoice
    """
    test_string = "M0-A SJ1-A M1-B SJ0-B CE1-A CE0-A"
    blockchain_lang_runner({0: 1, 1: 0}, test_string)


def test_ignore_zero_weight_block(blockchain_lang_runner):
    """ Tests that the forkchoice ignores zero weight blocks """
    # for more info about test, see
    # https://gist.github.com/naterush/8d8f6ec3509f50939d7911d608f912f4
    test_string = (
        "M0-A1 M0-A2 CE0-A2 M1-B1 M1-B2 SJ3-B2 M3-D1 CE3-D1 "
        "SJ3-A2 CE3-A2 M3-D2 SJ2-B1 CE2-B1 M2-C1 CE2-C1 SJ1-D1 "
        "SJ1-D2 SJ1-C1 CE1-B2"
    )
    blockchain_lang_runner({0: 10, 1: 9, 2: 8, 3: 0.5}, test_string)


def test_reverse_message_arrival_order_forkchoice(blockchain_lang_runner):
    test_string = (
        "M0-A SJ1-A M1-B SJ0-B M0-C SJ1-C M1-D SJ0-D M1-E SJ0-E "
        "SJ2-E CE2-E SJ3-A SJ3-B SJ3-C SJ3-D SJ3-E CE3-E"
    )
    blockchain_lang_runner({0: 5, 1: 6, 2: 7, 3: 8.1}, test_string)


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
