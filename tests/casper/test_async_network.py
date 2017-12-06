CONSTANT = 10


#
# Helpers
#
def constant(sender, receiver):
    return CONSTANT


def zero(sender, receiver):
    return 0


#
# Tests
#
def test_send(network, from_validator, to_validator):
    message = from_validator.make_new_message()
    assert network.message_queues[to_validator].qsize() == 0

    network.send(to_validator, message)
    assert network.message_queues[to_validator].qsize() == 1


def test_send_zero_delay(network, from_validator, to_validator):
    network.delay = zero
    message = from_validator.make_new_message()
    network.send(to_validator, message)

    assert network.message_queues[to_validator].qsize() == 1
    assert network.message_queues[to_validator].peek()[0] == network.time


def test_send_constant_delay(network, from_validator, to_validator):
    network.delay = constant
    message = from_validator.make_new_message()
    network.send(to_validator, message)

    assert network.message_queues[to_validator].qsize() == 1
    assert network.message_queues[to_validator].peek()[0] == network.time + CONSTANT


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


def test_receive_before_delay(network, to_validator, from_validator):
    network.delay = constant
    message = from_validator.make_new_message()
    network.send(to_validator, message)

    assert network.message_queues[to_validator].qsize() == 1
    assert network.message_queues[to_validator].peek()[0] > network.time

    assert network.receive(to_validator) is None
    assert network.message_queues[to_validator].qsize() == 1


def test_receive_at_delay(network, from_validator, to_validator):
    network.delay = constant
    message = from_validator.make_new_message()
    network.send(to_validator, message)

    assert network.message_queues[to_validator].qsize() == 1
    network.time += CONSTANT
    assert network.message_queues[to_validator].peek()[0] == network.time

    assert network.receive(to_validator) is message
    assert network.message_queues[to_validator].qsize() == 0


def test_receive_after_delay(network, from_validator, to_validator):
    network.delay = constant
    message = from_validator.make_new_message()
    network.send(to_validator, message)

    assert network.message_queues[to_validator].qsize() == 1
    network.time += CONSTANT*3
    assert network.message_queues[to_validator].peek()[0] < network.time

    assert network.receive(to_validator) is message
    assert network.message_queues[to_validator].qsize() == 0


def test_receive_multiple_after_delay(network, from_validator, to_validator):
    num_messages_to_send = 3
    network.delay = constant
    messages = []
    for i in range(num_messages_to_send):
        message = from_validator.make_new_message()
        network.send(to_validator, message)
        messages.append(message)

    assert network.message_queues[to_validator].qsize() == num_messages_to_send
    network.time += CONSTANT*3

    for i in range(num_messages_to_send):
        message = network.receive(to_validator)
        assert message in messages
        messages.remove(message)


def test_receive_all_after_delay(network, from_validator, to_validator):
    num_messages_to_send = 3
    network.delay = constant
    messages = []
    for i in range(num_messages_to_send):
        message = from_validator.make_new_message()
        network.send(to_validator, message)
        messages.append(message)

    assert network.message_queues[to_validator].qsize() == num_messages_to_send
    network.time += CONSTANT*3

    received_messages = network.receive_all(to_validator)
    assert set(messages) == set(received_messages)
