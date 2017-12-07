import random as r
import pytest

from casper.protocols.blockchain.blockchain_protocol import BlockchainProtocol
from casper.network import Network
from casper.networks import (
    ConstantDelayNetwork,
    SynchronousNetwork
)
from casper.validator import Validator

from simulations.testing_language import TestLangCBC
from simulations.utils import generate_random_gaussian_validator_set


def pytest_addoption(parser):
    parser.addoption("--report", action="store_true", default=False,
                     help="plot TestLangCBC tests")


def run_test_lang_with_reports(test_string, weights):
    TestLangCBC(weights, BlockchainProtocol, True).parse(test_string)


def run_test_lang_without_reports(test_string, weights):
    TestLangCBC(weights, BlockchainProtocol, False).parse(test_string)


def random_gaussian_validator_set_from_protocol(protocol=BlockchainProtocol):
    return generate_random_gaussian_validator_set(protocol)


@pytest.fixture(autouse=True)
def reset_blockchain_protocol(request):
    BlockchainProtocol.genesis_block = None


@pytest.fixture
def report(request):
    return request.config.getoption("--report")


@pytest.fixture
def test_lang_runner(report):
    if report:
        return run_test_lang_with_reports
    else:
        return run_test_lang_without_reports


@pytest.fixture
def generate_validator_set():
    return random_gaussian_validator_set_from_protocol


@pytest.fixture
def validator_set():
    return random_gaussian_validator_set_from_protocol(BlockchainProtocol)


@pytest.fixture
def validator(validator_set):
    return r.choice(list(validator_set.validators))


@pytest.fixture
def to_from_validators(validator_set):
    return r.sample(
        validator_set.validators,
        2
    )


@pytest.fixture
def to_validator(to_from_validators):
    return to_from_validators[0]


@pytest.fixture
def from_validator(to_from_validators):
    return to_from_validators[1]


@pytest.fixture
def network(validator_set):
    return SynchronousNetwork(validator_set)


@pytest.fixture
def synchronous_network(validator_set):
    return SynchronousNetwork(validator_set)


@pytest.fixture
def constant_delay_network(validator_set):
    return ConstantDelayNetwork(validator_set)


@pytest.fixture
def global_view(network):
    return network.global_view
