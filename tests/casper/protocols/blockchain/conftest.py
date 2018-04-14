import random
import pytest

from casper.protocols.blockchain.blockchain_protocol import BlockchainProtocol
from casper.validator_set import ValidatorSet

from simulations.json_generator import generate_blockchain_json

@pytest.fixture
def blockchain_class():
    return BlockchainProtocol


@pytest.fixture
def blockchain_instantiated(blockchain_class, test_weight):
    return blockchain_class(
        generate_blockchain_json(exe_str='', weights=test_weight),
        False,
        False,
        1
    )


@pytest.fixture
def blockchain_creator(blockchain_class):
    def creator(weights):
        return blockchain_class(
            generate_blockchain_json(exe_str='', weights=weights),
            False,
            False,
            1
        )
    return creator


@pytest.fixture
def blockchain_validator_set(test_weight, blockchain_class):
    return ValidatorSet(test_weight, blockchain_class.View, blockchain_class.Message)


@pytest.fixture
def blockchain_validator(blockchain_validator_set):
    return random.choice(list(blockchain_validator_set))


@pytest.fixture
def create_block(blockchain_validator):
    def c_block(estimate):
        return BlockchainProtocol.Message(estimate, {}, blockchain_validator, 0, 0)
    return c_block
