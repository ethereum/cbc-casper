import pytest

from casper.network import Network
from casper.block import Block
from casper.justification import Justification
import casper.settings as s
from casper.testing_language import TestLangCBC

TEST_STRING = 'B0-A'
TEST_WEIGHT = [i for i in range(5, 0, -1)]

def test_init_non_empty_string():
    TestLangCBC(TEST_STRING, [1])

def test_init_fail_empty_string():
    test_string = ('')
    with pytest.raises(Exception):
        TestLangCBC(test_string, [1])

@pytest.mark.parametrize(
    'weight_list, num_val, weight_dict, total_weight',
    [
        ([i for i in range(10)], 10, {i: i for i in range(10)}, 45),
        ([i for i in range(9, -1, -1)], 10, {i: 9 - i for i in range(10)}, 45),
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
def test_make_blocks_makes_new_blocks_adds_global_view(test_string, num_blocks, exception):
    test_lang = TestLangCBC(test_string, TEST_WEIGHT)

    if exception == '':
        test_lang.parse()
        assert len(test_lang.network.global_view.messages) == num_blocks
    else:
        with pytest.raises(Exception, match=exception):
            test_lang.parse()


# NOTE: None means the block is not named by the testing language
# this means the block was a init block, or was created by round robin
@pytest.mark.parametrize(
    'test_string, block_justification',
    [
        ('B0-A', {'A': {0: None}}),
        ('B0-A S1-A B1-B', {'B': {0: 'A', 1: None}}),
        ('RR0-A', {'A': {i: None for i in range(5)}}),
        ('RR0-A B0-B S1-B B1-C', {'C': {0:'B', 1:None, 2:None, 3:None, 4:None}}),
        ('B0-A S1-A B1-B S2-B B2-C S3-C B3-D S4-D B4-E',
            {'E': {0:'A', 1:'B', 2:'C', 3:'D', 4:None}}),
        ('B0-A S1-A B1-B S2-B B2-C S3-C B3-D S4-D B4-E S0-E B0-F',
            {'F': {0:'A', 1:'B', 2:'C', 3:'D', 4:'E'}})

    ]
)
def test_make_block_builds_on_entire_view(test_string, block_justification):
    test_lang = TestLangCBC(test_string, TEST_WEIGHT)
    test_lang.parse()

    for b in block_justification:
        block = test_lang.blocks[b]
        assert len(block.justification.latest_messages) == len(block_justification[b].keys())
        for v in block_justification[b]:
            block_in_justification = block_justification[b][v]
            if block_in_justification:
                assert test_lang.blocks[block_in_justification] == block.justification.latest_messages[v]


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


@pytest.mark.parametrize(
    'test_string, num_messages_per_view, message_keys',
    [
        ('B0-A S1-A', {0:2, 1:3}, {0: ['A'], 1: ['A']}),
        ('B0-A S1-A S2-A S3-A S4-A', {0:2, 1:3, 2:3, 3:3, 4:3}, {i: ['A'] for i in range(5)}),
        ('B0-A S1-A B1-B S2-B B2-C S3-C B3-D S4-D B4-E', {0:2, 1:4, 2:6, 3:8, 4:10},
            {0: ['A'], 1: ['A', 'B'], 2: ['A', 'B', 'C'], 3: ['A', 'B', 'C', 'D'], 4: ['A', 'B', 'C', 'D', 'E']}),
        ('B0-A B0-B B0-C B0-D B0-E', {0:6, 1:1, 2:1, 3:1, 4:1},
            {0: ['A', 'B', 'C', 'D', 'E'], 1:[], 2:[], 3:[], 4:[]}),
    ]
)
def test_send_block_updates_val_view(test_string, num_messages_per_view, message_keys):
    test_lang = TestLangCBC(test_string, TEST_WEIGHT)
    test_lang.parse()

    for v in num_messages_per_view:
        assert len(test_lang.network.validators[v].view.messages) == num_messages_per_view[v]
        for m in message_keys[v]:
            assert test_lang.blocks[m] in test_lang.network.validators[v].view.messages


@pytest.mark.parametrize(
    'test_string, num_messages_per_view, other_val_seen',
    [
        ('RR0-A', {0:10, 1:4, 2:6, 3:8, 4:10}, {0:[0,1,2,3,4], 1:[0,1], 2:[0,1,2], 3:[0,1,2,3], 4:[0,1,2,3,4]}),
        ('RR0-A RR0-B', {0:15, 1:12, 2:13, 3:14, 4:15}, {i:[0,1,2,3,4] for i in range(5)}),
        ('B0-A S1-A B1-B RR1-C', {0:12, 1:12, 2:7, 3:9, 4:11},
            {0:[0,1,2,3,4], 1:[0,1,2,3,4], 2:[0,1,2], 3:[0,1,2,3], 4:[0,1,2,3,4]}),
        ('RR0-A B0-B S1-B RR1-C', {0:16, 1:16, 2:13, 3:14, 4:15}, {i:[0,1,2,3,4] for i in range(5)}),
    ]
)
def test_round_robin_updates_val_view(test_string, num_messages_per_view, other_val_seen):
    test_lang = TestLangCBC(test_string, TEST_WEIGHT)
    test_lang.parse()

    for v in num_messages_per_view:
        assert len(test_lang.network.validators[v].view.messages) == num_messages_per_view[v]
        assert len(test_lang.network.validators[v].view.latest_messages) == len(other_val_seen[v])
        for v in other_val_seen[v]:
            assert v in test_lang.network.validators[v].view.latest_messages




@pytest.mark.parametrize(
    'test_string, val_forkchoice',
    [
        ('B0-A S1-A H1-A', {1: 'A'}),
        ('RR0-A', {0: 'A'}),
        ('B0-A S1-A S2-A S3-A S4-A H1-A H2-A H3-A H4-A', {i: 'A' for i in range(5)}),
        ('RR0-A RR0-B H0-B', {0: 'B'}),
        ('B0-A S1-A B1-B S2-B B2-C S3-C B3-D S4-D B4-E H0-A H1-B H2-C H3-D H4-E',
            {0:'A', 1:'B', 2:'C', 3:'D', 4:'E'})
    ]
)
def test_head_equals_block_checks_forkchoice(test_string, val_forkchoice):
    test_lang = TestLangCBC(test_string, TEST_WEIGHT)
    test_lang.parse()

    for v in val_forkchoice:
        assert test_lang.blocks[val_forkchoice[v]] == test_lang.network.validators[v].estimate()
