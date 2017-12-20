"""The language testing module ... """
import pytest

from testing_languages.blockchain_test_lang import BlockchainTestLang
from casper.network import Network
from casper.validator_set import ValidatorSet


def test_init_creates_state_lang(test_weight):
    blockchain_lang = BlockchainTestLang(test_weight, False)

    blockchain_lang.messages
    blockchain_lang.plot_tool

    assert isinstance(blockchain_lang.network, Network)
    assert isinstance(blockchain_lang.validator_set, ValidatorSet)

    assert len(blockchain_lang.validator_set) == len(test_weight)

    # should only have seen the genesis block
    for validator in blockchain_lang.validator_set:
        assert len(validator.view.justified_messages) == 1


def test_check_estimate_passes_on_valid_assertions(test_weight):
    blockchain_lang = BlockchainTestLang(test_weight, False)
    blockchain_lang.parse('M0-A S1-A S2-A S3-A S4-A CE0-A CE1-A CE2-A CE3-A CE4-A')

    forkchoice = blockchain_lang.messages['A']

    for validator in blockchain_lang.validator_set:
        assert validator.estimate() == forkchoice


@pytest.mark.parametrize(
    'test_string',
    [
        ('M0-A S1-A M1-B CE1-A'),
        ('M0-A M1-B CE1-A'),
        ('M0-A M0-B S1-B CE1-B'),
        ('M0-A S1-A S2-A S3-A S4-A CE0-A CE1-A CE2-A CE3-A CE4-A M0-B CE0-A'),
    ]
)
def test_check_estimate_fails_on_invalid_assertions(test_weight, test_string):
    blockchain_lang = BlockchainTestLang(test_weight, False)

    with pytest.raises(AssertionError):
        blockchain_lang.parse(test_string)


def test_check_safe_passes_on_valid_assertions(test_weight):
    blockchain_lang = BlockchainTestLang(test_weight, False)
    blockchain_lang.parse('RR0-A RR0-B RR0-C RR0-D CS0-A CS1-A CS2-A CS3-A CS4-A')

    safe_block = blockchain_lang.messages['A']

    for validator in blockchain_lang.validator_set:
        assert not safe_block.conflicts_with(validator.view.last_finalized_block)


@pytest.mark.parametrize(
    'test_string',
    [
        ('M0-A CS0-A'),
        ('M0-A CS1-A'),
        ('M0-A S1-A S2-A S3-A S4-A CS4-A'),
        ('RR0-A CS0-A'),
        ('RR0-A RR0-B RR0-C RR0-D RR0-E RR0-F CS1-F'),
    ]
)
def test_check_safe_fails_on_invalid_assertions(test_weight, test_string):
    blockchain_lang = BlockchainTestLang(test_weight, False)

    with pytest.raises(AssertionError):
        blockchain_lang.parse(test_string)


def test_check_unsafe_passes_on_valid_assertions(test_weight):
    blockchain_lang = BlockchainTestLang(test_weight, False)
    blockchain_lang.parse('M0-A CU0-A')

    not_safe_block = blockchain_lang.messages['A']

    for validator in blockchain_lang.validator_set:
        assert not_safe_block.conflicts_with(validator.view.last_finalized_block)


@pytest.mark.parametrize(
    'test_string',
    [
        ('RR0-A RR0-B RR0-C RR0-D CU0-A'),
        ('M0-A RR0-B RR0-C RR0-D CE1-A CS1-A CU0-A'),
    ]
)
def test_check_unsafe_fails_on_invalid_assertions(test_weight, test_string):
    blockchain_lang = BlockchainTestLang(test_weight, False)

    with pytest.raises(AssertionError):
        blockchain_lang.parse(test_string)
