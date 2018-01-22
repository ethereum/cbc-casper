import random
import pytest

from state_languages.blockchain_test_lang import BlockchainTestLang
from casper.protocols.blockchain.blockchain_protocol import BlockchainProtocol


@pytest.fixture
def blockchain_lang(report, test_weight):
    return BlockchainTestLang(test_weight, report)


@pytest.fixture
def blockchain_lang_runner(report):
    def runner(weights, test_string):
        BlockchainTestLang(weights, report).parse(test_string)
    return runner


@pytest.fixture
def blockchain_lang_creator(report):
    def creator(weights):
        return BlockchainTestLang(weights, report)
    return creator


@pytest.fixture
def blockchain_validator_set(generate_validator_set):
    return generate_validator_set(BlockchainProtocol)


@pytest.fixture
def blockchain_validator(blockchain_validator_set):
    return random.choice(list(blockchain_validator_set))


@pytest.fixture
def block(empty_just, blockchain_validator):
    return BlockchainProtocol.Message(None, empty_just, blockchain_validator, 0, 0)


@pytest.fixture
def create_block(empty_just, blockchain_validator):
    def c_block(estimate):
        return BlockchainProtocol.Message(estimate, empty_just, blockchain_validator, 0, 0)
    return c_block
