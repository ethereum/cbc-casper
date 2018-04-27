import pytest

from simulations.network_delay import (
    no_delay,
    step_delay,
    constant_delay,
    random_delay,
    gaussian_delay
)

DELAY_FUNCTIONS = [no_delay, step_delay, constant_delay, random_delay, gaussian_delay]

@pytest.fixture(params=DELAY_FUNCTIONS)
def delay_function(request):
    return request.param
