import pytest

from state_languages.blockchain_test_lang import BlockchainTestLang
from state_languages.integer_test_lang import IntegerTestLang
from state_languages.binary_test_lang import BinaryTestLang


@pytest.fixture
def blockchain_lang(report, test_weight):
    return BlockchainTestLang(test_weight, report)


@pytest.fixture
def blockchain_lang_runner(report):
    def runner(weights, test_string):
        BlockchainTestLang(weights, report).parse(test_string)
    return runner


@pytest.fixture
def binary_lang_creator(report):
    def creator(weights):
        return BinaryTestLang(weights, report)
    return creator


@pytest.fixture
def blockchain_lang_creator(report):
    def creator(weights):
        return BlockchainTestLang(weights, report)
    return creator
