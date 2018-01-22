import random
import pytest

from casper.protocols.blockchain.blockchain_protocol import BlockchainProtocol


@pytest.fixture
def blockchain_validator(generate_validator_set):
    return random.choice(list(generate_validator_set(BlockchainProtocol)))


@pytest.fixture
def block(empty_just, blockchain_validator):
    return BlockchainProtocol.Message(None, empty_just, blockchain_validator, 0, 0)


@pytest.fixture
def create_block(empty_just, blockchain_validator):
    def c_block(estimate):
        return BlockchainProtocol.Message(estimate, empty_just, blockchain_validator, 0, 0)
    return c_block
