"""The block testing module ..."""
import copy

import pytest

from casper.protocols.blockchain.block import Block
from casper.validator import Validator

from state_languages.blockchain_test_lang import BlockchainTestLang


@pytest.mark.parametrize(
    'estimate, is_valid',
    [
        (None, True),
        ('block', False),
        (0, False),
        (True, False),
    ]
)
def test_accepts_valid_estimates(estimate, is_valid, block):
    if estimate == 'block':
        Block.is_valid_estimate(block) == is_valid

    assert Block.is_valid_estimate(estimate) == is_valid


@pytest.mark.parametrize(
    'estimate_one, estimate_two, conflicts',
    [
        (None, 'prev', False),
        (None, None, True),
    ]
)
def test_conflicts_with(estimate_one, estimate_two, conflicts, create_block):
    bet_one = create_block(estimate_one)
    if estimate_two == 'prev':
        estimate_two = bet_one
    bet_two = create_block(estimate_two)

    assert bet_one.conflicts_with(bet_two) == conflicts


def test_equality_of_copies_off_genesis(validator, empty_just):
    block = Block(None, empty_just, validator, 0, 0)

    shallow_copy = copy.copy(block)

    assert block == shallow_copy


@pytest.mark.skip(reason="current deepcopy bug")
def test_equality_of_copies_of_non_genesis(report):
    test_string = "M0-A SJ1-A M1-B SJ0-B M0-C SJ1-C M1-D SJ0-D CE0-D"
    test_lang = BlockchainTestLang({0: 10, 1: 11}, report)
    test_lang.parse(test_string)

    for message in test_lang.messages.values():
        shallow_copy = copy.copy(message)
        deep_copy = copy.deepcopy(message)

        assert message == shallow_copy
        assert message == deep_copy
        assert shallow_copy == deep_copy


def test_non_equality_of_copies_off_genesis(empty_just):
    validator_0 = Validator("v0", 10)
    validator_1 = Validator("v1", 11)

    block_0 = Block(None, empty_just, validator_0, 0, 0)
    block_1 = Block(None, empty_just, validator_1, 0, 0)

    assert block_0 != block_1


def test_unique_block_creation_in_test_lang(report):
    test_string = "M0-A SJ1-A M1-B SJ0-B M0-C SJ1-C M1-D SJ0-D CE0-D"
    test_lang = BlockchainTestLang({0: 10, 1: 11}, report)
    test_lang.parse(test_string)

    num_equal = 0
    for message1 in test_lang.messages:
        for message2 in test_lang.messages:
            if message1 == message2:
                num_equal += 1
                continue

            assert message1 != message2

    assert num_equal == len(test_lang.messages)


def test_is_in_blockchain__separate_genesis(empty_just):
    validator_0 = Validator("v0", 10)
    validator_1 = Validator("v1", 11)

    block_0 = Block(None, empty_just, validator_0, 0, 0)
    block_1 = Block(None, empty_just, validator_1, 0, 0)

    assert not block_0.is_in_blockchain(block_1)
    assert not block_1.is_in_blockchain(block_0)


def test_is_in_blockchain__test_lang(report):
    test_string = "M0-A SJ1-A M1-B SJ0-B M0-C SJ1-C M1-D SJ0-D CE0-D"
    test_lang = BlockchainTestLang({0: 11, 1: 10}, report)
    test_lang.parse(test_string)

    prev = test_lang.messages['A']
    for b in ['B', 'C', 'D']:
        block = test_lang.messages[b]
        assert prev.is_in_blockchain(block)
        assert not block.is_in_blockchain(prev)

        prev = block


@pytest.mark.parametrize(
    'test_string, weights, block_heights',
    [
        (
            "M0-A SJ1-A M1-B SJ0-B M0-C SJ1-C M1-D SJ0-D CE0-D",
            {0: 11, 1: 10},
            {"A": 2, "B": 3, "C": 4, "D": 5}
        ),
        (
            "M0-A SJ1-A M1-B SJ0-B M0-C SJ1-C M1-D SJ0-D CE0-D",
            {0: 1, 1: 10},
            {"A": 2, "B": 3, "C": 4, "D": 5}
        ),
        (
            "M0-A SJ1-A M0-B SJ1-B M1-C SJ0-C SJ2-C M2-D SJ0-D M0-E M1-F SJ0-F CE0-E",
            {0: 11, 1: 10, 2: 500},
            {"A": 2, "B": 3, "C": 4, "D": 5, "E": 6, "F": 5}
        ),
    ]
)
def test_block_height(blockchain_lang_creator, test_string, weights, block_heights):
    test_lang = blockchain_lang_creator(weights)
    test_lang.parse(test_string)

    for block_name in block_heights:
        block = test_lang.messages[block_name]
        assert block.height == block_heights[block_name]
