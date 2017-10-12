import pytest

from casper.network import Network
from casper.block import Block
from casper.justification import Justification
import casper.settings as s
from casper.testing_language import TestLangCBC

TEST_STRING = 'B0-A'
TEST_WEIGHT = [i for i in xrange(4, -1, -1)]

def test_init_non_empty_string():
    TestLangCBC(TEST_STRING, [1])

def test_init_fail_empty_string():
    test_string = ('')
    with pytest.raises(Exception):
        TestLangCBC(test_string, [1])

@pytest.mark.parametrize(
    'weight_list, num_val, weight_dict, total_weight',
    [
        ([i for i in xrange(10)], 10, {i: i for i in xrange(10)}, 45),
        ([i for i in xrange(9, -1, -1)], 10, {i: 9 - i for i in xrange(10)}, 45),
        ([0], 1, {0: 0}, 0),
        ([], 0, {}, 0),
    ]
)
def test_init_update_settings(weight_list, num_val, weight_dict, total_weight):
    TestLangCBC(TEST_STRING, weight_list)

    assert len(s.WEIGHTS) == num_val
    assert s.WEIGHTS == weight_dict
    assert s.TOTAL_WEIGHT == total_weight

def test_init_creates_network():
    test_lang = TestLangCBC(TEST_STRING, TEST_WEIGHT)

    assert isinstance(test_lang.network, Network)

def test_init_validators_create_blocks():
    test_lang = TestLangCBC(TEST_STRING, TEST_WEIGHT)

    assert len(test_lang.network.global_view.messages) == len(TEST_WEIGHT)

    for v in test_lang.network.validators:
        assert len(test_lang.network.validators[v].view.messages) == 1
        assert len(test_lang.network.validators[v].view.latest_messages) == 1
        assert test_lang.network.validators[v].view.latest_messages[v].estimate == None

@pytest.mark.parametrize(
    'test_string, valid_tokens, error',
    [
        ('B0-A', True, None),
        ('B0-A S1-A', True, None),
        ('B0-A S1-A U1-A', True, None),
        ('B0-A S1-A H1-A', True, None),
        ('B0-A RR0-B RR0-C C0-A', True, None),
        ('R', True, None),
        ('A-B', False, KeyError),
        ('BA0-A, S1-A', False, ValueError),
        ('BA0-A S1-A', False, KeyError),
        ('RR0-A-A', False, ValueError),
        ('B0-A S1-A T1-A', False, KeyError),
        ('RR0-AB1-A', False, ValueError),
        ('RRR', False, KeyError),
        ('A0-A S1-A', False, KeyError),
    ]
)
def test_parse_only_valid_tokens(test_string, valid_tokens, error):
    test_lang = TestLangCBC(test_string, TEST_WEIGHT)

    if valid_tokens:
        test_lang.parse()
    else:
        with pytest.raises(error):
            test_lang.parse()


@pytest.mark.parametrize(
    'test_string, val_weights, valid_validators',
    [
        ('B0-A B1-B B2-C B3-D B4-E', TEST_WEIGHT, True),
        ('B0-A S1-A S2-A S3-A S4-A', TEST_WEIGHT, True),
        ('B0-A S1-A U1-A', [1, 2], True),
        ('B0-A S1-A H1-A', [2, 1], True),
        ('RR0-A RR0-B C0-A', [2,1], True),
        ('B5-A', TEST_WEIGHT, False),
        ('B0-A S1-A', [1], False),
        ('B0-A S1-A S2-A S3-A S4-A', [0], False),
        ('B4-A S5-A', TEST_WEIGHT, False),
        ('B0-A S1-A U2-A', [1, 2], False),
        ('B0-A S1-A H2-A', [2, 1], False),
        ('RR0-A RR0-B C2-A', [2, 1], False),
    ]
)
def test_parse_only_valid_validators(test_string, val_weights, valid_validators):
    test_lang = TestLangCBC(test_string, val_weights)

    if valid_validators:
        test_lang.parse()
    else:
        with pytest.raises(Exception, match='Validator'):
            test_lang.parse()
