import pytest

from casper.network import Network
from casper.testing_language import TestLangCBC
from casper.validator import Validator
from simulations.utils import generate_random_validator_set


def pytest_addoption(parser):
    parser.addoption("--report", action="store_true", default=False,
                     help="plot TestLangCBC tests")


def run_test_lang_with_reports(test_string, weights):
    TestLangCBC(weights, True).parse(test_string)


def run_test_lang_without_reports(test_string, weights):
    TestLangCBC(weights, False).parse(test_string)


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
def validator_set():
    return generate_random_validator_set()


@pytest.fixture
def validator():
    return Validator("Name", 15.5)


@pytest.fixture
def network(validator_set):
    network = Network(validator_set)
    network.random_initialization()
    return network
