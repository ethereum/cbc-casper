import pytest


def test_justification_stores_hash(protocol_instantiated):
    protocol_instantiated.execute('M-0-A SJ-1-A M-1-B')

    validator_0 = protocol_instantiated.global_validator_set.get_validator_by_name(0)
    validator_1 = protocol_instantiated.global_validator_set.get_validator_by_name(1)

    justification = validator_1.justification()

    assert justification[validator_0] == protocol_instantiated.messages['A'].hash
    assert justification[validator_1] == protocol_instantiated.messages['B'].hash


def test_justification_includes_justified_messages(protocol_instantiated):
    protocol_instantiated.execute('M-0-A M-0-B S-1-B M-1-C')

    validator_0 = protocol_instantiated.global_validator_set.get_validator_by_name(0)
    validator_1 = protocol_instantiated.global_validator_set.get_validator_by_name(1)

    justification = validator_1.justification()

    assert protocol_instantiated.messages["A"].hash not in justification.values()
    assert protocol_instantiated.messages["B"].hash not in justification.values()
    assert justification[validator_1] == protocol_instantiated.messages['C'].hash

    protocol_instantiated.execute('SJ-1-B')

    justification = validator_1.justification()
    assert justification[validator_0] == protocol_instantiated.messages['B'].hash
    assert justification[validator_1] == protocol_instantiated.messages['C'].hash


def test_add_justified_message(protocol_instantiated):
    protocol_instantiated.execute('M-0-A M-0-B SJ-1-A')
    validator_0 = protocol_instantiated.global_validator_set.get_validator_by_name(0)
    validator_1 = protocol_instantiated.global_validator_set.get_validator_by_name(1)
    assert protocol_instantiated.messages['A'] in validator_0.view.justified_messages.values()
    assert protocol_instantiated.messages['A'] in validator_1.view.justified_messages.values()
    assert protocol_instantiated.messages['B'] in validator_0.view.justified_messages.values()
    assert protocol_instantiated.messages['B'] not in validator_1.view.justified_messages.values()


@pytest.mark.parametrize(
    'test_string, justified_messages, unjustified_messages',
    [
        ('M-0-A M-0-B S-1-B', [['A', 'B'], []], [[], ['B']]),
        ('M-0-A M-0-B S-1-B SJ-1-A', [['A', 'B'], ['A', 'B']], [[], []]),
        ('M-0-A M-0-B M-0-C S-1-C S-1-B', [['A', 'B', 'C'], []], [[], ['B', 'C']]),
    ]
)
def test_only_add_justified_messages(test_string, justified_messages, unjustified_messages, protocol_instantiated):
    protocol_instantiated.execute(test_string)

    for v in protocol_instantiated.global_validator_set:
        if v.name >= 2:
            continue

        for message in justified_messages[v.name]:
            assert protocol_instantiated.messages[message] in v.view.justified_messages.values()
            assert protocol_instantiated.messages[message] not in v.view.pending_messages.values()

        for message in unjustified_messages[v.name]:
            assert protocol_instantiated.messages[message] not in v.view.justified_messages.values()
            assert protocol_instantiated.messages[message] in v.view.pending_messages.values()


@pytest.mark.parametrize(
    'test_string, justified_messages, unjustified_messages, resolving_string',
    [
        (
            'M-0-A M-0-B S-1-B',
            [['A', 'B'], []],
            [[], ['B']],
            'SJ-1-A'
        ),
        (
            'M-0-A SJ-1-A M-0-B M-0-C M-0-D M-0-E S-1-E',
            [['A', 'B', 'C', 'D', 'E'], ['A'], []],
            [[], [], ['E']],
            'S-1-B S-1-C S-1-D'
        ),
        (
            'M-0-A SJ-1-A M-0-B M-0-C M-0-D M-0-E S-1-E',
            [['A', 'B', 'C', 'D', 'E'], ['A'], []],
            [[], [], ['E']],
            'S-1-D S-1-B S-1-C'
        ),
    ]
)
def test_resolve_message_when_justification_arrives(
        test_string,
        justified_messages,
        unjustified_messages,
        resolving_string,
        protocol_instantiated
    ):
    protocol_instantiated.execute(test_string)

    for validator in protocol_instantiated.global_validator_set:
        if validator.name >= 2:
            continue

        idx = validator.name
        view = validator.view

        for message in justified_messages[idx]:
            assert protocol_instantiated.messages[message] in view.justified_messages.values()
            assert protocol_instantiated.messages[message] not in view.pending_messages.values()

        for message in unjustified_messages[idx]:
            assert protocol_instantiated.messages[message] not in view.justified_messages.values()
            assert protocol_instantiated.messages[message] in view.pending_messages.values()

    protocol_instantiated.execute(resolving_string)

    for validator in protocol_instantiated.global_validator_set:
        if validator.name >= 2:
            continue
        idx = validator.name
        view = validator.view

        for message in justified_messages[idx]:
            assert protocol_instantiated.messages[message] in view.justified_messages.values()
            assert protocol_instantiated.messages[message] not in view.pending_messages.values()

        for message in unjustified_messages[idx]:
            assert protocol_instantiated.messages[message] in view.justified_messages.values()
            assert protocol_instantiated.messages[message] not in view.pending_messages.values()



def test_multiple_messages_arriving_resolve(protocol_instantiated):
    test_string = "M-0-A SJ-1-A M-0-B M-0-C M-0-D M-0-E M-0-F S-1-F"
    protocol_instantiated.execute(test_string)

    val_1 = protocol_instantiated.global_validator_set.get_validator_by_name(1)
    assert protocol_instantiated.messages['F'] in val_1.view.pending_messages.values()

    val_1.receive_messages(protocol_instantiated.global_view.justified_messages.values())
    assert protocol_instantiated.messages['F'] in val_1.view.justified_messages.values()
