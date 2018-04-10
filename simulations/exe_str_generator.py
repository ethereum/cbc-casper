"""The simulution utils module ... """
from random import (
    randint
)

from casper.utils import get_random_str


def make_com(comm, vali, name):
    return comm + '-' + str(vali) + '-' + name


def generate_execution(num_validators, num_rounds, network_delay_func, get_creators):
    execution_string = ''
    commands_on_round = {r: [] for r in range(num_rounds)}
    sent_from = {v: set() for v in range(num_validators)}

    for curr_round in range(num_rounds):
        creators = get_creators()

        for creator in creators:
            msg_name = get_random_str(10)
            commands_on_round[curr_round].append(make_com('M', creator, msg_name))

            for receiver in range(num_validators):
                delivery_round = curr_round + network_delay_func(creator, receiver, curr_round)
                if delivery_round >= num_rounds:
                    continue

                if receiver not in sent_from[creator]:
                    send_command = 'SJ'
                    sent_from[creator].add(receiver)
                else:
                    send_command = 'S'

                commands_on_round[delivery_round].append(
                    make_com(send_command, receiver, msg_name)
                )

        for command in commands_on_round[curr_round]:
            execution_string += command + ' '

    return execution_string


def generate_random_execution(num_validators, num_rounds, network_delay_func):
    """An execution in which a random validator creates a message each round"""
    def random_creator():
        """Returns a random validator to create a message"""
        return [randint(0, num_validators - 1)]

    return generate_execution(num_validators, num_rounds, network_delay_func, random_creator), 1


def generate_full_execution(num_validators, num_rounds, network_delay_func):
    def all_creators():
        return range(num_validators)

    return generate_execution(num_validators, num_rounds, network_delay_func, all_creators), num_validators


def generate_rrob_execution(num_validators, num_rounds, network_delay_func):
    curr_creator = 0
    def rrob_creator():
        nonlocal curr_creator
        to_return = curr_creator
        curr_creator = (curr_creator + 1) % num_validators
        return [to_return]

    return generate_execution(num_validators, num_rounds, network_delay_func, rrob_creator), 1


SELECT_EXECUTION_GENERATOR = {
    'rand': generate_random_execution,
    'full': generate_full_execution,
    'rrob': generate_rrob_execution
}
