import pytest

from casper.blockchain.blockchain_protocol import BlockchainProtocol
from casper.network import Network
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
def validator():
    return Validator("Name", 15.5)


@pytest.fixture
def network(validator_set):
    network = Network(validator_set)
    network.random_initialization()
    return network
