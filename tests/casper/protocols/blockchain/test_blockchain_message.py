"""The block testing module ..."""
import copy

import pytest

from casper.protocols.blockchain.block import Block
from casper.validator import Validator


@pytest.mark.parametrize(
    'estimate, is_valid',
    [
        (None, True),
        (0, False),
        (True, False),
    ]
)
def test_accepts_valid_estimates(estimate, is_valid):
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


def test_equality_of_copies_off_genesis(blockchain_validator):
    block = Block(None, {}, blockchain_validator, 0, 0)

    shallow_copy = copy.copy(block)

    assert block == shallow_copy


def test_unique_block_creation(blockchain_creator):
    execution_string = "M-0-A SJ-1-A M-1-B SJ-0-B M-0-C SJ-1-C M-1-D SJ-0-D"
    protocol = blockchain_creator([10, 11])
    protocol.execute(execution_string)

    num_equal = 0
    for message1 in protocol.messages.values():
        for message2 in protocol.messages.values():
            if message1 == message2:
                num_equal += 1
                continue

            assert message1 != message2

    assert num_equal == len(protocol.messages)


def test_is_in_blockchain_separate_genesis(blockchain_validator_set):
    validator_0 = blockchain_validator_set.get_validator_by_name(0)
    validator_1 = blockchain_validator_set.get_validator_by_name(1)

    block_0 = Block(None, {}, validator_0, 0, 0)
    block_1 = Block(None, {}, validator_1, 0, 0)

    assert not block_0.is_in_blockchain(block_1)
    assert not block_1.is_in_blockchain(block_0)


def test_is_in_blockchain_test_lang(blockchain_creator):
    execution_string = "M-0-A SJ-1-A M-1-B SJ-0-B M-0-C SJ-1-C M-1-D SJ-0-D"
    protocol = blockchain_creator([10, 11])
    protocol.execute(execution_string)


    prev = protocol.messages['A']
    for b in ['B', 'C', 'D']:
        block = protocol.messages[b]
        assert prev.is_in_blockchain(block)
        assert not block.is_in_blockchain(prev)

        prev = block


@pytest.mark.parametrize(
    'test_string, weights, block_heights',
    [
        (
            "M-0-A SJ-1-A M-1-B SJ-0-B M-0-C SJ-1-C M-1-D SJ-0-D",
            [11, 10],
            {"A": 2, "B": 3, "C": 4, "D": 5}
        ),
        (
            "M-0-A SJ-1-A M-1-B SJ-0-B M-0-C SJ-1-C M-1-D SJ-0-D",
            [1, 10],
            {"A": 2, "B": 3, "C": 4, "D": 5}
        ),
        (
            "M-0-A SJ-1-A M-0-B SJ-1-B M-1-C SJ-0-C SJ-2-C M-2-D SJ-0-D M-0-E M-1-F SJ-0-F",
            [11, 10, 500],
            {"A": 2, "B": 3, "C": 4, "D": 5, "E": 6, "F": 5}
        ),
    ]
)
def test_block_height(blockchain_creator, test_string, weights, block_heights):
    protocol = blockchain_creator(weights)
    protocol.execute(test_string)

    for block_name in block_heights:
        block = protocol.messages[block_name]
        assert block.height == block_heights[block_name]
