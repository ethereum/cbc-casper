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
    'test_string, val_weights, exception',
    [
        ('B0-A B1-B B2-C B3-D B4-E', TEST_WEIGHT, ''),
        ('B0-A S1-A S2-A S3-A S4-A', TEST_WEIGHT, ''),
        ('B0-A S1-A U1-A', [1, 2], ''),
        ('B0-A S1-A H1-A', [2, 1], ''),
        ('RR0-A RR0-B C0-A', [2,1], ''),
        ('B5-A', TEST_WEIGHT, 'Validator'),
        ('B0-A S1-A', [1], 'Validator'),
        ('B0-A S1-A S2-A S3-A S4-A', [0], 'Validator'),
        ('B4-A S5-A', TEST_WEIGHT, 'Validator'),
        ('B0-A S1-A U2-A', [1, 2], 'Validator'),
        ('B0-A S1-A H2-A', [2, 1], 'Validator'),
        ('RR0-A RR0-B C2-A', [2, 1], 'Validator'),
        ('B0-A S1-B', TEST_WEIGHT, 'Block'),
        ('B0-A S1-A U1-B', TEST_WEIGHT, 'Block'),
        ('B0-A S1-A H1-B', TEST_WEIGHT, 'Block'),
        ('B0-A RR0-B RR0-C C0-D', TEST_WEIGHT, 'Block'),
    ]
)
def test_parse_only_valid_val_and_blocks(test_string, val_weights, exception):
    test_lang = TestLangCBC(test_string, val_weights)

    if exception == '':
        test_lang.parse()
    else:
        with pytest.raises(Exception, match=exception):
            test_lang.parse()


# NOTE: network.global_view.messages starts with 5 messages from random_initialization
@pytest.mark.parametrize(
    'test_string, num_blocks, exception',
    [
        ('B0-A', 6, ''),
        ('B0-A S1-A', 6, ''),
        ('B0-A S1-A U1-A B1-B', 7, ''),
        ('B0-A S1-A H1-A B1-B', 7, ''),
        ('B0-A RR0-B RR0-C C0-A B0-D', 17, ''),
        ('B0-A B1-B B2-C B3-D B4-E', 10, ''),
        ('B0-A S1-A S2-A S3-A S4-A', 6, ''),
        ('RR0-A RR0-B', 15, ''),
        ('B0-A B1-A', 6, 'already exists'),
        ('B0-A S1-A S2-A S3-A S4-A B4-B B4-A', 6, 'already exists'),
        ('RR0-A RR0-A', 15, 'already exists'),
    ]
)
def test_make_blocks_makes_only_new_blocks(test_string, num_blocks, exception):
    test_lang = TestLangCBC(test_string, TEST_WEIGHT)

    if exception == '':
        test_lang.parse()
        assert len(test_lang.network.global_view.messages) == num_blocks
    else:
        with pytest.raises(Exception, match=exception):
            test_lang.parse()

# NOTE: network.global_view.messages starts with 5 messages from random_initialization
@pytest.mark.parametrize(
    'test_string, exception',
    [
        ('B0-A S1-A', ''),
        ('B0-A S1-A S2-A S3-A S4-A', ''),
        ('B0-A S1-A S1-A', 'has already seen block'),
        ('B0-A S0-A', 'has already seen block'),
        ('RR0-A RR0-B S0-A', 'has already seen block'),
    ]
)
def test_send_block_sends_only_existing_blocks(test_string, exception):
    test_lang = TestLangCBC(test_string, TEST_WEIGHT)

    if exception == '':
        test_lang.parse()
    else:
        with pytest.raises(Exception, match=exception):
            test_lang.parse()

def test_send_block_updates_view_one_message():
    test_string = 'B0-A S1-A'
    test_lang = TestLangCBC(test_string, TEST_WEIGHT)
    test_lang.parse()

    block_a = test_lang.blocks['A']
    assert block_a in test_lang.network.validators[1].view.messages
    assert block_a == test_lang.network.validators[1].view.latest_messages[0]


def test_send_block_updates_view_many_messages():
    test_string = 'B0-A S1-A B1-B S2-B B2-C S3-C B3-D S4-D'
    test_lang = TestLangCBC(test_string, TEST_WEIGHT)
    test_lang.parse()

    assert len(test_lang.network.validators[4].view.messages) == 9
    for v in test_lang.network.validators:
        assert v in test_lang.network.validators[4].view.latest_messages
    for b in test_lang.blocks:
        assert test_lang.blocks[b] in test_lang.network.validators[4].view.messages


def test_round_robin_updates_latest_messages():
    test_string = 'RR0-A'
    test_lang = TestLangCBC(test_string, TEST_WEIGHT)
    test_lang.parse()

    for v in test_lang.network.validators:
        if v == 0:
            assert len(test_lang.network.validators[v].view.messages) == 10
            assert len(test_lang.network.validators[v].view.latest_messages) == s.NUM_VALIDATORS
        else:
            assert len(test_lang.network.validators[v].view.messages) == 2 * (v + 1)
            assert len(test_lang.network.validators[v].view.latest_messages) == v + 1
            for v1 in test_lang.network.validators:
                if v1 > v:
                    assert v1 not in test_lang.network.validators[v].view.latest_messages
                else:
                    assert v1 in test_lang.network.validators[v].view.latest_messages


def test_round_robin_builds_off_most_recent_block():
    test_string = 'B0-A B0-B B0-C B0-D RR0-E'
    test_lang = TestLangCBC(test_string, TEST_WEIGHT)
    test_lang.parse()

    for v in test_lang.network.validators:
        if v == 0:
            assert len(test_lang.network.validators[v].view.messages) == 14
            assert len(test_lang.network.validators[v].view.latest_messages) == s.NUM_VALIDATORS
        else:
            assert len(test_lang.network.validators[v].view.messages) == 2 * (v + 3)
            assert len(test_lang.network.validators[v].view.latest_messages) == v + 1
            for v1 in test_lang.network.validators:
                if v1 > v:
                    assert v1 not in test_lang.network.validators[v].view.latest_messages
                else:
                    assert v1 in test_lang.network.validators[v].view.latest_messages


    block_on_block_d = False
    for b in test_lang.blocks:
        block = test_lang.blocks[b]
        if block.estimate == test_lang.blocks['D']:
            block_on_block_d = True

    assert block_on_block_d

# test round robin off of most recent block recieved.





# test that creating blocks adds them to the global view, and validator view

# test blocks make include all previous blocks recieved

# test that sending blocks sends the correct block

#


# test that


# test that report does not generate
