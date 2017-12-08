"""The network testing module ... """
from casper.network import Network


def test_new_network(validator_set):
    network = Network(validator_set)
    assert network.validator_set == validator_set
    assert len(network.global_view.justified_messages) == 1


def test_send(network, from_validator, to_validator):
    message = from_validator.make_new_message()
    assert network.message_queues[to_validator].qsize() == 0

    network.send(to_validator, message)
    assert network.message_queues[to_validator].qsize() == 1


def test_send_adds_to_global_view(network, global_view, from_validator, to_validator):
    message = from_validator.make_new_message()
    num_justified = len(global_view.justified_messages)
    network.send(to_validator, message)

    assert len(global_view.justified_messages) == num_justified + 1


def test_send_zero_delay(no_delay_network, from_validator, to_validator):
    message = from_validator.make_new_message()
    no_delay_network.send(to_validator, message)

    message_queue = no_delay_network.message_queues[to_validator]
    assert message_queue.qsize() == 1
    assert message_queue.peek()[0] == no_delay_network.time


def test_send_constant_delay(constant_delay_network, from_validator, to_validator):
    network = constant_delay_network
    message = from_validator.make_new_message()
    network.send(to_validator, message)

    message_queue = network.message_queues[to_validator]
    assert message_queue.qsize() == 1
    assert message_queue.peek()[0] == network.time + network.CONSTANT


def test_send_to_all(network, from_validator):
    message = from_validator.make_new_message()
    for validator in network.validator_set:
        assert network.message_queues[validator].qsize() == 0

    network.send_to_all(message)
    assert network.message_queues[from_validator].qsize() == 0
    for validator in network.validator_set:
        if validator == from_validator:
            continue
        message_queue = network.message_queues[validator]
        assert message_queue.qsize() == 1
        assert message_queue.queue[0][1] == message


def test_receive_empty(network, validator):
    assert network.message_queues[validator].qsize() == 0
    assert network.receive(validator) is None


def test_receive_before_delay(constant_delay_network, to_validator, from_validator):
    network = constant_delay_network
    message = from_validator.make_new_message()
    network.send(to_validator, message)

    message_queue = network.message_queues[to_validator]
    assert message_queue.qsize() == 1
    assert message_queue.peek()[0] > constant_delay_network.time

    assert network.receive(to_validator) is None
    assert network.message_queues[to_validator].qsize() == 1


def test_receive_at_delay(constant_delay_network, from_validator, to_validator):
    network = constant_delay_network
    message = from_validator.make_new_message()
    network.send(to_validator, message)

    assert network.message_queues[to_validator].qsize() == 1
    network.time += network.CONSTANT
    assert network.message_queues[to_validator].peek()[0] == network.time

    assert network.receive(to_validator) is message
    assert network.message_queues[to_validator].qsize() == 0


def test_receive_after_delay(constant_delay_network, from_validator, to_validator):
    network = constant_delay_network
    message = from_validator.make_new_message()
    network.send(to_validator, message)

    assert network.message_queues[to_validator].qsize() == 1
    network.time += network.CONSTANT * 3
    assert network.message_queues[to_validator].peek()[0] < network.time

    assert network.receive(to_validator) is message
    assert network.message_queues[to_validator].qsize() == 0


def test_receive_multiple_after_delay(constant_delay_network, from_validator, to_validator):
    network = constant_delay_network
    num_messages_to_send = 3
    messages = []
    for i in range(num_messages_to_send):
        message = from_validator.make_new_message()
        network.send(to_validator, message)
        messages.append(message)

    assert network.message_queues[to_validator].qsize() == num_messages_to_send
    network.time += network.CONSTANT * 3

    for i in range(num_messages_to_send):
        message = network.receive(to_validator)
        assert message in messages
        messages.remove(message)


def test_receive_all_available_after_delay(constant_delay_network, from_validator, to_validator):
    network = constant_delay_network
    num_messages_to_send = 3
    messages = []
    for i in range(num_messages_to_send):
        message = from_validator.make_new_message()
        network.send(to_validator, message)
        messages.append(message)

    assert network.message_queues[to_validator].qsize() == num_messages_to_send
    network.time += network.CONSTANT * 3

    received_messages = network.receive_all_available(to_validator)
    assert set(messages) == set(received_messages)
