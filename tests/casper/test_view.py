import pytest

from casper.abstract_view import AbstractView
from casper.blockchain.block import Block
from simulations.testing_language import TestLangCBC


TEST_WEIGHT = {0: 10, 1: 11}


def test_new_view():
    view = AbstractView()

    assert not any(view.justified_messages)
    assert not view.latest_messages
    assert not any(view.justification())


def test_justification_stores_hash():
    test_lang = TestLangCBC(TEST_WEIGHT)
    test_lang.parse('B0-A S1-A B1-B')

    validator_0 = test_lang.validator_set.get_validator_by_name(0)
    validator_1 = test_lang.validator_set.get_validator_by_name(1)

    justification = validator_1.view.justification()

    assert len(justification) == 2
    assert not isinstance(justification[validator_0], Block)
    assert not isinstance(justification[validator_1], Block)
    assert justification[validator_0] == test_lang.blocks['A'].hash
    assert justification[validator_1] == test_lang.blocks['B'].hash


def test_justification_includes_justified_messages():
    test_lang = TestLangCBC(TEST_WEIGHT)
    test_lang.parse('B0-A B0-B P1-B B1-C')

    validator_0 = test_lang.validator_set.get_validator_by_name(0)
    validator_1 = test_lang.validator_set.get_validator_by_name(1)

    justification = validator_1.view.justification()

    assert len(justification) == 1
    assert validator_0 not in justification
    assert justification[validator_1] == test_lang.blocks['C'].hash

    test_lang.parse('S1-B')

    justification = validator_1.view.justification()

    assert len(justification) == 2
    assert justification[validator_0] == test_lang.blocks['B'].hash
    assert justification[validator_1] == test_lang.blocks['C'].hash


def test_add_justified_message():
    test_lang = TestLangCBC(TEST_WEIGHT)
    test_lang.parse('B0-A B0-B S1-A')
    validator_0 = test_lang.validator_set.get_validator_by_name(0)
    validator_1 = test_lang.validator_set.get_validator_by_name(1)
    assert test_lang.blocks['A'] in validator_0.view.justified_messages.values()
    assert test_lang.blocks['A'] in validator_1.view.justified_messages.values()
    assert test_lang.blocks['B'] in validator_0.view.justified_messages.values()
    assert test_lang.blocks['B'] not in validator_1.view.justified_messages.values()


@pytest.mark.parametrize(
    'test_string, justified_messages, unjustified_messages',
    [
        ('B0-A B0-B P1-B', [['A', 'B'], []], [[], ['B']]),
        ('B0-A B0-B P1-B S1-A', [['A', 'B'], ['A', 'B']], [[], []]),
        ('B0-A B0-B B0-C P1-C P1-B', [['A', 'B', 'C'], []], [[], ['B', 'C']]),
    ]
)
def test_only_add_justified_messages(test_string, justified_messages, unjustified_messages):
    test_lang = TestLangCBC(TEST_WEIGHT)
    test_lang.parse(test_string)

    for validator in test_lang.validator_set:
        idx = validator.name

        for message in justified_messages[idx]:
            assert test_lang.blocks[message] in validator.view.justified_messages.values()
            assert test_lang.blocks[message] not in validator.view.pending_messages.values()

        for message in unjustified_messages[idx]:
            assert test_lang.blocks[message] not in validator.view.justified_messages.values()
            assert test_lang.blocks[message] in validator.view.pending_messages.values()


@pytest.mark.parametrize(
    'weight, test_string, justified_messages, unjustified_messages, resolving_string',
    [
        (
            TEST_WEIGHT,
            'B0-A B0-B P1-B',
            [['A', 'B'], []],
            [[], ['B']],
            'S1-A'
        ),
        (
            {0: 10, 1: 9, 2: 8},
            'RR0-A B0-B S1-B B1-C P2-C',
            [['A', 'B'], ['A', 'B'], []],
            [[], [], ['C']],
            'P2-B'
        ),
        (
            TEST_WEIGHT,
            'B0-A S1-A B0-B B0-C B0-D B0-E P1-E',
            [['A', 'B', 'C', 'D', 'E'], ['A'], []],
            [[], [], ['E']],
            'P1-B P1-C P1-D'
        ),
        (
            TEST_WEIGHT,
            'B0-A S1-A B0-B B0-C B0-D B0-E P1-E',
            [['A', 'B', 'C', 'D', 'E'], ['A'], []],
            [[], [], ['E']],
            'P1-D P1-B P1-C'
        ),
    ]
)
def test_resolve_message_when_justification_arrives(weight, test_string, justified_messages, unjustified_messages, resolving_string):
    test_lang = TestLangCBC(weight)
    test_lang.parse(test_string)

    for validator in test_lang.validator_set:
        idx = validator.name

        for message in justified_messages[idx]:
            assert test_lang.blocks[message] in validator.view.justified_messages.values()
            assert test_lang.blocks[message] not in validator.view.pending_messages.values()

        for message in unjustified_messages[idx]:
            assert test_lang.blocks[message] not in validator.view.justified_messages.values()
            assert test_lang.blocks[message] in validator.view.pending_messages.values()

    test_lang.parse(resolving_string)

    for validator in test_lang.validator_set:
        idx = validator.name

        for message in justified_messages[idx]:
            assert test_lang.blocks[message] in validator.view.justified_messages.values()
            assert test_lang.blocks[message] not in validator.view.pending_messages.values()

        for message in unjustified_messages[idx]:
            assert test_lang.blocks[message] in validator.view.justified_messages.values()
            assert test_lang.blocks[message] not in validator.view.pending_messages.values()



def test_multiple_messages_arriving_resolve():
    test_string = "B0-A S1-A B0-B B0-C B0-D B0-E B0-F P1-F"
    test_lang = TestLangCBC(TEST_WEIGHT)
    test_lang.parse(test_string)

    validator_1 = test_lang.validator_set.get_validator_by_name(1)

    assert len(validator_1.view.justified_messages) == 3
    assert len(validator_1.view.pending_messages) == 1
    assert test_lang.blocks['F'] in validator_1.view.pending_messages.values()

    validator_1.receive_messages(test_lang.network.global_view.justified_messages.values())

    assert len(validator_1.view.justified_messages) == 8
