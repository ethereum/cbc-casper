"""The block testing module ..."""
import copy

import pytest

from casper.protocols.concurrent.block import Block
from casper.protocols.concurrent.concurrent_protocol import ConcurrentProtocol


@pytest.mark.parametrize(
    'estimate, is_valid',
    [
        ({'blocks': {None}, 'inputs': [], 'outputs': []}, True),
        ({'blocks': {None}, 'inputs': [1, 2, 3], 'outputs': [4, 5, 6]}, True),
        ({'blocks': {None}, 'inputs': []}, False),
        ({'blocks': {None}, 'outputs': []}, False),
        ({'blocks': {None}}, False),
        ({'blocks': [], 'inputs': [], 'outputs': []}, False),
        ({'inputs': [], 'outputs': []}, False),
        (0, False),
        (True, False),
    ]
)
def test_accepts_valid_estimates(estimate, is_valid):
    assert Block.is_valid_estimate(estimate) == is_valid
