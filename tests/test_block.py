import copy

from casper.block import Block
from casper.justification import Justification
import casper.settings as s
from casper.testing_language import TestLangCBC


def test_equality_of_copies_off_genesis():
    s.update([10])  # necessary due to assertions during block creation
    block = Block(None, Justification(), 0)

    shallow_copy = copy.copy(block)
    deep_copy = copy.deepcopy(block)

    assert block == shallow_copy
    assert block == deep_copy
    assert shallow_copy == deep_copy


def test_equality_of_copies_of_non_genesis(report):
    test_string = "B0-A S1-A B1-B S0-B B0-C S1-C B1-D S0-D H0-D"
    testLang = TestLangCBC(test_string, [10, 11], report)
    testLang.parse()

    for b in testLang.blocks:
        shallow_copy = copy.copy(b)
        deep_copy = copy.deepcopy(b)

        assert b == shallow_copy
        assert b == deep_copy
        assert shallow_copy == deep_copy


def test_non_equality_of_copies_off_genesis():
    s.update([10, 11])
    block_0 = Block(None, Justification(), 0)
    block_1 = Block(None, Justification(), 1)

    assert block_0 != block_1


def test_unique_block_creation_in_test_lang(report):
    test_string = "B0-A S1-A B1-B S0-B B0-C S1-C B1-D S0-D H0-D"
    testLang = TestLangCBC(test_string, [10, 11], report)
    testLang.parse()

    num_equal = 0
    for b in testLang.blocks:
        for b1 in testLang.blocks:
            if b1 == b:
                num_equal += 1
                continue

            assert b != b1

    assert num_equal == len(testLang.blocks)


def test_is_in_blockchain__separate_genesis():
    s.update([10, 11])
    block_0 = Block(None, Justification(), 0)
    block_1 = Block(None, Justification(), 1)

    assert not block_0.is_in_blockchain(block_1)
    assert not block_1.is_in_blockchain(block_0)


def test_is_in_blockchain__test_lang(report):
    test_string = "B0-A S1-A B1-B S0-B B0-C S1-C B1-D S0-D H0-D"
    testLang = TestLangCBC(test_string, [11, 10], report)
    testLang.parse()

    prev = testLang.blocks['A']
    for b in ['B', 'C', 'D']:
        block = testLang.blocks[b]
        assert prev.is_in_blockchain(block)
        assert not block.is_in_blockchain(prev)

        prev = block
