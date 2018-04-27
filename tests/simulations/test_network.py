"""The network testing module ... """
from simulations.network_delay import (
    no_delay,
    step_delay,
    constant_delay,
    random_delay,
    gaussian_delay,
    CONSTANT
)


def test_meets_interface(delay_function):
    assert callable(delay_function)
    delay_function(0, 0, 0)


def test_no_delay():
    for i in range(10):
        delay = no_delay(i, i, i)
        assert delay == 0


def test_step_delay():
    for i in range(10):
        delay = step_delay(i, i, i)
        assert delay == 1


def test_constant_delay():
    for i in range(10):
        delay = constant_delay(i, i, i)
        assert delay == CONSTANT


def test_random_delay():
    for i in range(10):
        delay = random_delay(i, i, i)
        assert delay in range(CONSTANT + 1)


def test_gaussian_delay():
    for i in range(10):
        delay = gaussian_delay(i, i, i)
