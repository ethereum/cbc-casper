import pytest

from casper.abstract_view import AbstractView
from casper.protocols.blockchain.block import Block
from testing_languages.blockchain_test_lang import BlockchainTestLang


TEST_WEIGHT = {0: 10, 1: 11}


def test_new_view():
    view = AbstractView()

    assert not any(view.justified_messages)
    assert not any(view.latest_messages)


def test_justification_stores_hash():
    test_lang = BlockchainTestLang(TEST_WEIGHT)
    test_lang.parse('M0-A SJ1-A M1-B')

    validator_0 = test_lang.validator_set.get_validator_by_name(0)
    validator_1 = test_lang.validator_set.get_validator_by_name(1)

    justification = validator_1.justification()

    assert len(justification) == 2
    assert not isinstance(justification[validator_0], Block)
    assert not isinstance(justification[validator_1], Block)
    assert justification[validator_0] == test_lang.messages['A'].hash
    assert justification[validator_1] == test_lang.messages['B'].hash


def test_justification_includes_justified_messages():
    test_lang = BlockchainTestLang(TEST_WEIGHT)
    test_lang.parse('M0-A M0-B SJ1-B M1-C')

    validator_0 = test_lang.validator_set.get_validator_by_name(0)
    validator_1 = test_lang.validator_set.get_validator_by_name(1)

    justification = validator_1.justification()

    assert len(justification) == 2
    assert test_lang.messages["A"].hash not in justification.values()
    assert test_lang.network.global_view.genesis_block.hash in justification.values()
    assert justification[validator_1] == test_lang.messages['C'].hash

    test_lang.parse('SJ1-B')

    justification = validator_1.justification()

    assert len(justification) == 2
    assert justification[validator_0] == test_lang.messages['B'].hash
    assert justification[validator_1] == test_lang.messages['C'].hash


def test_add_justified_message():
    test_lang = BlockchainTestLang(TEST_WEIGHT)
    test_lang.parse('M0-A M0-B SJ1-A')
    validator_0 = test_lang.validator_set.get_validator_by_name(0)
    validator_1 = test_lang.validator_set.get_validator_by_name(1)
    assert test_lang.messages['A'] in validator_0.view.justified_messages.values()
    assert test_lang.messages['A'] in validator_1.view.justified_messages.values()
    assert test_lang.messages['B'] in validator_0.view.justified_messages.values()
    assert test_lang.messages['B'] not in validator_1.view.justified_messages.values()


@pytest.mark.parametrize(
    'test_string, justified_messages, unjustified_messages',
    [
        ('M0-A M0-B S1-B', [['A', 'B'], []], [[], ['B']]),
        ('M0-A M0-B S1-B SJ1-A', [['A', 'B'], ['A', 'B']], [[], []]),
        ('M0-A M0-B M0-C S1-C S1-B', [['A', 'B', 'C'], []], [[], ['B', 'C']]),
    ]
)
def test_only_add_justified_messages(test_string, justified_messages, unjustified_messages):
    test_lang = BlockchainTestLang(TEST_WEIGHT)
    test_lang.parse(test_string)

    for validator in test_lang.validator_set:
        idx = validator.name

        for message in justified_messages[idx]:
            assert test_lang.messages[message] in validator.view.justified_messages.values()
            assert test_lang.messages[message] not in validator.view.pending_messages.values()

        for message in unjustified_messages[idx]:
            assert test_lang.messages[message] not in validator.view.justified_messages.values()
            assert test_lang.messages[message] in validator.view.pending_messages.values()


@pytest.mark.parametrize(
    'weight, test_string, justified_messages, unjustified_messages, resolving_string',
    [
        (
            TEST_WEIGHT,
            'M0-A M0-B S1-B',
            [['A', 'B'], []],
            [[], ['B']],
            'SJ1-A'
        ),
        (
            {0: 10, 1: 9, 2: 8},
            'RR0-A M0-B SJ1-B M1-C S2-C',
            [['A', 'B'], ['A', 'B'], []],
            [[], [], ['C']],
            'S2-B'
        ),
        (
            TEST_WEIGHT,
            'M0-A SJ1-A M0-B M0-C M0-D M0-E S1-E',
            [['A', 'B', 'C', 'D', 'E'], ['A'], []],
            [[], [], ['E']],
            'S1-B S1-C S1-D'
        ),
        (
            TEST_WEIGHT,
            'M0-A SJ1-A M0-B M0-C M0-D M0-E S1-E',
            [['A', 'B', 'C', 'D', 'E'], ['A'], []],
            [[], [], ['E']],
            'S1-D S1-B S1-C'
        ),
    ]
)
def test_resolve_message_when_justification_arrives(weight, test_string, justified_messages, unjustified_messages, resolving_string):
    test_lang = BlockchainTestLang(weight)
    test_lang.parse(test_string)

    for validator in test_lang.validator_set:
        idx = validator.name

        for message in justified_messages[idx]:
            assert test_lang.messages[message] in validator.view.justified_messages.values()
            assert test_lang.messages[message] not in validator.view.pending_messages.values()

        for message in unjustified_messages[idx]:
            assert test_lang.messages[message] not in validator.view.justified_messages.values()
            assert test_lang.messages[message] in validator.view.pending_messages.values()

    test_lang.parse(resolving_string)

    for validator in test_lang.validator_set:
        idx = validator.name

        for message in justified_messages[idx]:
            assert test_lang.messages[message] in validator.view.justified_messages.values()
            assert test_lang.messages[message] not in validator.view.pending_messages.values()

        for message in unjustified_messages[idx]:
            assert test_lang.messages[message] in validator.view.justified_messages.values()
            assert test_lang.messages[message] not in validator.view.pending_messages.values()



def test_multiple_messages_arriving_resolve():
    test_string = "M0-A SJ1-A M0-B M0-C M0-D M0-E M0-F S1-F"
    test_lang = BlockchainTestLang(TEST_WEIGHT)
    test_lang.parse(test_string)

    validator_1 = test_lang.validator_set.get_validator_by_name(1)

    assert len(validator_1.view.justified_messages) == 2
    assert len(validator_1.view.pending_messages) == 1
    assert test_lang.messages['F'] in validator_1.view.pending_messages.values()

    validator_1.receive_messages(test_lang.network.global_view.justified_messages.values())

    assert len(validator_1.view.justified_messages) == 7
