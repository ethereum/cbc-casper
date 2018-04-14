import pytest

from casper.protocol import Protocol

from simulations.exe_str_generator import (
    generate_random_execution,
    generate_full_execution,
    generate_rrob_execution
)

from simulations.network_delay import no_delay


def test_random_execution():
    execution_str, _ = generate_random_execution(5, 5, no_delay)
    print(execution_str)

    sent = 0
    for token in execution_str.split():
        comm, _, _, _ = Protocol.parse_token(token)

        if sent == 5:
            assert comm == 'M'
            sent = 0

        if comm == 'S' or comm == 'SJ':
            sent += 1


def test_round_robin_message_maker():
    execution_str, _ = generate_rrob_execution(5, 5, no_delay)

    sent = 0
    sender = 1
    for token in execution_str.split():
        comm, vali, _, _ = Protocol.parse_token(token)

        if sent == 5:
            assert comm == 'M'
            assert int(vali) == sender
            sender = (sender + 1) % 5
            sent = 0

        if comm == 'S' or comm == 'SJ':
            sent += 1


def test_full_message_maker():
    execution_str, _ = generate_full_execution(5, 5, no_delay)
    print(execution_str)

    current_comm = 'M'
    number = 0
    validator = 0

    for token in execution_str.split():
        comm, vali, _, _ = Protocol.parse_token(token)

        number += 1
        if comm == 'M':
            assert comm == current_comm
        else:
            assert comm == 'S' or comm == 'SJ'

        if comm == 'M':
            assert int(vali) == validator
            validator = (validator + 1) % 5

        if number == 5 and current_comm == 'M':
            current_comm = 'S'
            number = 0
        elif number == 25 and current_comm == 'S':
            current_comm = 'M'
            number = 0


def test_no_final_message_maker():
    pass
