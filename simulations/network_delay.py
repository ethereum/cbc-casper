"""The simulution utils module ... """
import random

CONSTANT = 5
MU = 10
SIGMA = 5

def no_delay(sender, reciever, curr_round):
    """Messages deliver instantly"""
    return 0


def constant_delay(sender, reciever, curr_round):
    """Messages take a constant number of rounds to deliver"""
    return CONSTANT


def step_delay(sender, reciever, curr_round):
    """Messages take 1 round to deliver"""
    return 1


def random_delay(sender, reciever, curr_round):
    """Messages take a random amount of time to deliver"""
    return random.randint(0, CONSTANT)


def gaussian_delay(sender, reciever, curr_round):
    """Messages take a random amount of time to deliver
    (from a gaussian distribution)"""
    return round(random.gauss(MU, SIGMA).real)

SELECT_NETWORK_DELAY = {
    'no-delay': no_delay,
    'step': step_delay,
    'constant': constant_delay,
    'random': random_delay,
    'gaussian': gaussian_delay
}
