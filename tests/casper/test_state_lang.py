"""The language testing module ... """
import pytest

from state_languages.state_language import StateLanguage
from casper.network import Network


def test_init(protocol, test_weight):
    state_lang = StateLanguage(test_weight, protocol, False)

    assert isinstance(state_lang.plot_tool, protocol.PlotTool)
    assert len(state_lang.validator_set) == len(test_weight)
    assert state_lang.validator_set.validator_weights() == set(test_weight.values())
    assert state_lang.validator_set.weight() == sum(test_weight.values())

    assert isinstance(state_lang.network, Network)


def test_registers_handlers(protocol, test_weight):
    state_lang = StateLanguage(test_weight, protocol, False)

    assert callable(state_lang.make_message)
    assert callable(state_lang.make_invalid)
    assert callable(state_lang.send_message)
    assert callable(state_lang.plot)
    assert callable(state_lang.check_estimate)
    assert callable(state_lang.check_safe)
    assert callable(state_lang.check_unsafe)

    assert state_lang.make_message == state_lang.handlers['M']
    assert state_lang.make_invalid == state_lang.handlers['I']
    assert state_lang.send_message == state_lang.handlers['S']
    assert state_lang.plot == state_lang.handlers['P']
    assert state_lang.check_estimate == state_lang.handlers['CE']
    assert state_lang.check_safe == state_lang.handlers['CS']
    assert state_lang.check_unsafe == state_lang.handlers['CU']


@pytest.mark.parametrize(
    'handler, error',
    (
        ('M', KeyError),
        ('S', KeyError),
        ('I', KeyError),
        ('P', KeyError),
        ('CE', KeyError),
        ('CS', KeyError),
        ('CU', KeyError),
        ('CV', None),
        ('H', None),
        ('123-123', None),
    )
)
def test_allows_new_handlers_to_register(handler, error, protocol, test_weight, example_function):
    state_lang = StateLanguage(test_weight, protocol, False)

    if isinstance(error, type) and issubclass(error, Exception):
        with pytest.raises(error):
            state_lang.register_handler(handler, example_function)
        return

    state_lang.register_handler(handler, example_function)
    assert callable(state_lang.handlers[handler])
    assert state_lang.handlers[handler] == example_function


def test_init_validators_have_only_inital_messages(protocol, test_weight):
    state_lang = StateLanguage(test_weight, protocol, False)

    for validator in state_lang.network.validator_set:
        assert len(validator.view.justified_messages) == 1


@pytest.mark.parametrize(
    'test_string, error',
    [
        ('M0-A', None),
        ('M0-A S1-A', None),
        ('M0-A M0-B', None),
        ('M0-A M0-B S1-A S1-B', None),
        ('I1-B', NotImplementedError),
        ('A-B', ValueError),
        ('BA0-A, S1-A', KeyError),
        ('BA0-A S1-A', KeyError),
        ('RR0-A-A', ValueError),
        ('B0-A S1-A T1-A', KeyError),
        ('RR0-AB1-A', ValueError),
        ('RRR', ValueError),
        ('A0-A S1-A', KeyError),
    ]
)
def test_parse_only_valid_tokens(test_string, test_weight, error, protocol):
    state_lang = StateLanguage(test_weight, protocol, False)

    if isinstance(error, type) and issubclass(error, Exception):
        with pytest.raises(error):
            state_lang.parse(test_string)
        return

    state_lang.parse(test_string)


@pytest.mark.parametrize(
    'test_strings, error',
    [
        (['M0-A', 'S1-A'], None),
        (['M0-A', 'M0-B S1-A S1-B'], None),
        (['M0-A', 'I1-B'], NotImplementedError),
        (['M0-A', 'S1-A T1-A'], KeyError),
        (['M1-A', 'RR0-AB1-A'], ValueError),
    ]
)
def test_parse_only_valid_tokens_split_strings(test_strings, error, protocol, test_weight):
    state_lang = StateLanguage(test_weight, protocol, False)

    if isinstance(error, type) and issubclass(error, Exception):
        with pytest.raises(error):
            for test_string in test_strings:
                state_lang.parse(test_string)
        return

    for test_string in test_strings:
        state_lang.parse(test_string)


@pytest.mark.parametrize(
    'test_string, test_weight, exception',
    [
        ('M0-A M1-B M2-C M3-D M4-E', {i: 5 - i for i in range(5)}, ''),
        ('M0-A S1-A S2-A S3-A S4-A', {i: 5 - i for i in range(5)}, ''),
        ('M0-A S1-A', {0: 1, 1: 2}, ''),
        ('M5-A', {i: 5 - i for i in range(5)}, True),
        ('M0-A S1-A', {0: 1}, True),
        ('M0-A S1-A S2-A S3-A S4-A', {0: 0}, True),
        ('M4-A S5-A', {i: 5 - i for i in range(5)}, True),
        ('M0-A S1-B', {i: 5 - i for i in range(5)}, True),
        ('M0-A M1-A', {i: 5 - i for i in range(5)}, True),
    ]
)
def test_parse_only_valid_val_and_messages(test_string, test_weight, exception, protocol):
    state_lang = StateLanguage(test_weight, protocol, False)

    if exception:
        with pytest.raises(Exception):
            state_lang.parse(test_string)
        return

    state_lang.parse(test_string)


@pytest.mark.parametrize(
    'test_strings, test_weight, exception',
    [
        (['M0-A M1-B', 'M2-C M3-D M4-E'], {i: 5 - i for i in range(5)}, ''),
        (['M0-A S1-A', 'S2-A S3-A S4-A'], {i: 5 - i for i in range(5)}, ''),
        (['M0-A', 'S1-A'], {0: 1, 1: 2}, ''),
        (['M0-A', 'S1-A'], {0: 1}, True),
        (['M0-A S1-A', 'S2-A S3-A S4-A'], {0: 0}, True),
        (['M4-A', 'S5-A'], {i: 5 - i for i in range(5)}, True),
        (['M0-A', 'S1-B'], {i: 5 - i for i in range(5)}, True),
        (['M0-A', 'M1-A'], {i: 5 - i for i in range(5)}, True),
    ]
)
def test_parse_only_valid_val_and_messages_split_strings(test_strings, test_weight, exception, protocol):
    state_lang = StateLanguage(test_weight, protocol, False)

    if exception:
        with pytest.raises(Exception):
            for test_string in test_strings:
                state_lang.parse(test_string)
        return

    for test_string in test_strings:
        state_lang.parse(test_string)


@pytest.mark.parametrize(
    'test_string, num_blocks, exception',
    [
        ('M0-A', 1, ''),
        ('M0-A S1-A', 1, ''),
        ('M0-A S1-A M1-B', 2, ''),
        ('M0-A M1-B M2-C M3-D M4-E', 5, ''),
        ('M0-A S1-A S2-A S3-A S4-A', 1, ''),
        ('M0-A M1-A', None, 'already exists'),
        ('M0-A S1-A S2-A S3-A S4-A M4-B M4-A', None, 'already exists'),
    ]
)
def test_make_adds_to_global_view_(
        test_string,
        test_weight,
        num_blocks,
        exception,
        protocol
        ):
    state_lang = StateLanguage(test_weight, protocol, False)

    num_inital_blocks = len(state_lang.network.global_view.justified_messages)
    if exception:
        with pytest.raises(Exception, match=exception):
            state_lang.parse(test_string)
        return

    state_lang.parse(test_string)
    assert len(state_lang.network.global_view.justified_messages) == num_blocks + num_inital_blocks


@pytest.mark.parametrize(
    'test_string, block_justification',
    [
        ('M0-A', {'A': {0: "GEN"}}),
        ('M0-A S1-A M1-B', {'B': {0: 'A'}}),
        (
            'M0-A S1-A M1-B S2-A S2-B M2-C S3-A S3-B S3-C M3-D S4-A S4-B S4-C S4-D M4-E',
            {'E': {0: 'A', 1: 'B', 2: 'C', 3: 'D'}}
        ),
    ]
)
def test_make_messages_builds_on_view(test_string, block_justification, test_weight, genesis_protocol):
    state_lang = StateLanguage(test_weight, genesis_protocol, False)
    state_lang.parse(test_string)
    global_view = state_lang.network.global_view

    for b in block_justification:
        block = state_lang.messages[b]
        assert len(block.justification) == len(block_justification[b])
        for validator_name in block_justification[b]:
            block_in_justification = block_justification[b][validator_name]
            validator = state_lang.validator_set.get_validator_by_name(validator_name)

            if block_in_justification:
                message_hash = block.justification[validator]
                justification_message = global_view.justified_messages[message_hash]

                if block_in_justification == "GEN":
                    assert global_view.genesis_block == justification_message
                else:
                    assert state_lang.messages[block_in_justification] == justification_message


@pytest.mark.parametrize(
    'test_string, num_messages_per_view, message_keys',
    [
        (
            'M0-A S1-A',
            {0: 2, 1: 2},
            {0: ['A'], 1: ['A']}
        ),
        (
            'M0-A S1-A S2-A S3-A S4-A',
            {0: 2, 1: 2, 2: 2, 3: 2, 4: 2},
            {i: ['A'] for i in range(5)}
        ),
        (
            'M0-A S1-A M1-B S2-A S2-B M2-C S3-A S3-B S3-C M3-D S4-A S4-B S4-C S4-D M4-E',
            {0: 2, 1: 3, 2: 4, 3: 5, 4: 6},
            {
                0: ['A'],
                1: ['A', 'B'],
                2: ['A', 'B', 'C'],
                3: ['A', 'B', 'C', 'D'],
                4: ['A', 'B', 'C', 'D', 'E']
            }
        ),
        (
            'M0-A M0-B M0-C M0-D M0-E',
            {0: 6, 1: 1, 2: 1, 3: 1, 4: 1},
            {0: ['A', 'B', 'C', 'D', 'E'], 1: [], 2: [], 3: [], 4: []}
        ),
    ]
)
def test_send_updates_val_view_genesis_protocols(
        test_string,
        test_weight,
        num_messages_per_view,
        message_keys,
        genesis_protocol
    ):
    state_lang = StateLanguage(test_weight, genesis_protocol, False)
    state_lang.parse(test_string)

    for validator_name in num_messages_per_view:
        validator = state_lang.validator_set.get_validator_by_name(validator_name)
        assert len(validator.view.justified_messages) == num_messages_per_view[validator_name]
        for message_name in message_keys[validator_name]:
            assert state_lang.messages[message_name] in validator.view.justified_messages.values()
