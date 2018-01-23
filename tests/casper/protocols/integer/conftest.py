import random
import pytest

from state_languages.integer_test_lang import IntegerTestLang
from casper.protocols.integer.integer_protocol import IntegerProtocol


@pytest.fixture
def integer_lang(report, test_weight):
    return IntegerTestLang(test_weight, report)


@pytest.fixture
def integer_lang_runner(report):
    def runner(weights, test_string):
        IntegerTestLang(weights, report).parse(test_string)
    return runner


@pytest.fixture
def integer_lang_creator(report):
    def creator(weights):
        return IntegerTestLang(weights, report)
    return creator


@pytest.fixture
def integer_validator_set(generate_validator_set):
    return generate_validator_set(IntegerProtocol)


@pytest.fixture
def integer_validator(integer_validator_set):
    return random.choice(list(integer_validator_set))


@pytest.fixture
def bet(empty_just, integer_validator):
    return IntegerProtocol.Message(0, empty_just, integer_validator, 0, 0)


@pytest.fixture
def create_bet(empty_just, integer_validator):
    def c_bet(estimate):
        return IntegerProtocol.Message(estimate, empty_just, integer_validator, 0, 0)
    return c_bet
