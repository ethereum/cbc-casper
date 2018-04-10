import pytest

from simulations.network_delay import (
    no_delay,
    step_delay,
    constant_delay,
    random_delay,
    gaussian_delay
)

from state_languages.blockchain_test_lang import BlockchainTestLang
from state_languages.integer_test_lang import IntegerTestLang
from state_languages.binary_test_lang import BinaryTestLang

TEST_LANGS = [BlockchainTestLang, IntegerTestLang, BinaryTestLang]
DELAY_FUNCTIONS = [no_delay, step_delay, constant_delay, random_delay, gaussian_delay]


@pytest.fixture(params=TEST_LANGS)
def test_lang_creator(request, report):
    def creator(weights):
        return request.param(weights, report)
    return creator


@pytest.fixture(params=DELAY_FUNCTIONS)
def delay_function(request):
    return request.param
