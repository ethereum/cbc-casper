"""The language testing module tests the state language is parsed and use correctly"""
import pytest

from casper.protocol import Protocol

@pytest.mark.parametrize(
    'token, comm, vali, name, data',
    (
        ('M-0-A', 'M', '0', 'A', ''),
        ('S-0-A', 'S', '0', 'A', ''),
        ('SJ-0-A', 'SJ', '0', 'A', ''),
        ('ABC-123-A', 'ABC', '123', 'A', ''),
        ('M-0-A-()', 'M', '0', 'A', '()'),
        ('S-0-A-(ABC)', 'S', '0', 'A', '(ABC)'),
        ('SJ-0-A-(A,B,C)', 'SJ', '0', 'A', '(A,B,C)')
    )
)
def test_parses_valid_tokens(token, comm, vali, name, data):
    p_comm, p_vali, p_name, p_data = Protocol.parse_token(token)
    assert p_comm == comm
    assert p_vali == vali
    assert p_name == name
    assert p_data == data


@pytest.mark.parametrize(
    'token',
    (
        ('M-0-A-A-B'),
        ('M- 0-A'),
        ('M0-A'),
        ('S-0A')
    )
)
def test_errors_on_invalid_tokens(token):
    with pytest.raises(ValueError):
        Protocol.parse_token(token)


def test_make_new_messages(protocol_instantiated):
    protocol_instantiated.execute('M-0-A')
    assert protocol_instantiated.messages['A'].sender.name == 0


def test_make_fails_invalid_val(protocol_instantiated):
    with pytest.raises(KeyError):
        protocol_instantiated.execute('M-5-A')


def test_stops_overwriting_messages(protocol_instantiated):
    with pytest.raises(KeyError):
        protocol_instantiated.execute('M-0-A M-1-A')


def test_sends_existing_messages(protocol_instantiated):
    protocol_instantiated.execute('M-0-A SJ-1-A')
    message = protocol_instantiated.messages['A']
    receiver = protocol_instantiated.global_validator_set.get_validator_by_name(1)
    assert message in receiver.view.justified_messages.values()


def test_sends_does_not_justify(protocol_instantiated):
    protocol_instantiated.execute('M-0-A M-0-B S-1-B')
    message = protocol_instantiated.messages['B']
    receiver = protocol_instantiated.global_validator_set.get_validator_by_name(1)
    assert message in receiver.view.pending_messages.values()


def test_fails_send_nonexisting_messages(protocol_instantiated):
    with pytest.raises(KeyError):
        protocol_instantiated.execute('M-0-A S-1-B')


def test_send_and_justify(protocol_instantiated):
    protocol_instantiated.execute('M-0-A M-0-B SJ-1-B')
    message_a = protocol_instantiated.messages['A']
    message_b = protocol_instantiated.messages['B']
    receiver = protocol_instantiated.global_validator_set.get_validator_by_name(1)
    assert message_a in receiver.view.justified_messages.values()
    assert message_b in receiver.view.justified_messages.values()
