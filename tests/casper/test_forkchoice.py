"""The forkchoice testing module ... """
import pytest
import random as r

import casper.protocols.blockchain.forkchoice as forkchoice


def test_single_validator_correct_forkchoice(test_lang_runner):
    """ This tests that a single validator remains on their own chain """
    test_string = ""
    for i in range(100):
        test_string += "B0-" + str(i) + " " + "H0-" + str(i) + " "
    test_string = test_string[:-1]

    test_lang_runner(test_string, {0: 10})


def test_two_validators_round_robin_forkchoice(test_lang_runner):
    test_string = "B0-A S1-A B1-B S0-B B0-C S1-C B1-D S0-D H0-D R"
    test_lang_runner(test_string, {0: 10, 1: 11})


def test_many_val_round_robin_forkchoice(test_lang_runner):
    """
    Tests that during a perfect round robin,
    validators choose the one chain as their fork choice
    """
    test_string = ""
    for i in range(100):
        test_string += "B" + str(i % 10) + "-" + str(i) + " " \
                     + "S" + str((i+1) % 10) + "-" + str(i) + " " \
                     + "H" + str((i+1) % 10) + "-" + str(i) + " "
    test_string = test_string[:-1]

    test_lang_runner(
        test_string,
        {i: 10 - i + r.random() for i in range(10)}
    )


def test_fail_on_tie(test_lang_runner):
    """
    Tests that if there are two subsets of the validator
    set with the same weight, the forkchoice fails
    """
    test_string = "B1-A S0-A B0-B S1-B S2-A B2-C S1-C H1-C"
    with pytest.raises(AssertionError):
        test_lang_runner(test_string, {0: 5, 1: 6, 2: 5})


def test_ignore_zero_weight_validator(test_lang_runner):
    """
    Tests that a validator with zero weight
    will not affect the forkchoice
    """
    test_string = "B0-A S1-A B1-B S0-B H1-A H0-A"
    test_lang_runner(test_string, {0: 1, 1: 0})


def test_ignore_zero_weight_block(test_lang_runner):
    """ Tests that the forkchoice ignores zero weight blocks """
    # for more info about test, see
    # https://gist.github.com/naterush/8d8f6ec3509f50939d7911d608f912f4
    test_string = (
        "B0-A1 B0-A2 H0-A2 B1-B1 B1-B2 S3-B2 B3-D1 H3-D1 "
        "S3-A2 H3-A2 B3-D2 S2-B1 H2-B1 B2-C1 H2-C1 S1-D1 "
        "S1-D2 S1-C1 H1-B2"
    )
    test_lang_runner(test_string, {0: 10, 1: 9, 2: 8, 3: 0.5})


def test_reverse_message_arrival_order_forkchoice_four_val(test_lang_runner):
    test_string = (
        "B0-A S1-A B1-B S0-B B0-C S1-C B1-D S0-D B1-E S0-E "
        "S2-E H2-E S3-A S3-B S3-C S3-D S3-E H3-E"
    )
    test_lang_runner(test_string, {0: 5, 1: 6, 2: 7, 3: 8.1})


@pytest.mark.skip(reason="test not yet implemented")
def test_different_message_arrival_order_forkchoice_many_val():
    pass


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
