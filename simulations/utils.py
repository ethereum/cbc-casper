"""The simulution utils module contains utilities for
generating and running CBC Casper simulations"""
import random

from argparse import (
    ArgumentTypeError
)

from casper.protocols.blockchain.blockchain_protocol import BlockchainProtocol
from casper.protocols.binary.binary_protocol import BinaryProtocol
from casper.protocols.integer.integer_protocol import IntegerProtocol
from casper.protocols.order.order_protocol import OrderProtocol
from casper.protocols.concurrent.concurrent_protocol import ConcurrentProtocol
from casper.protocols.sharding.sharding_protocol import ShardingProtocol

SELECT_PROTOCOL = {
    'blockchain': BlockchainProtocol,
    'binary': BinaryProtocol,
    'integer': IntegerProtocol,
    'order': OrderProtocol,
    'concurrent': ConcurrentProtocol,
    'sharding': ShardingProtocol
}

BIG_INT = 1000000000000

def generate_random_gaussian_weights(
        num_validators=5,
        mu=60,
        sigma=40,
        min_weight=20
    ):
    """Generates random gaussian weights for validators"""
    return [
        max(min_weight, random.gauss(mu, sigma))
        + 1.0/(BIG_INT + random.uniform(0, 1)) + random.random()
        for _ in range(num_validators)
    ]


def str2bool(val):
    """Converts common boolean strings to booleans"""
    if val.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif val.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise ArgumentTypeError('{} cannot be converted to a boolean'.format(val))


def exestr(val):
    """Returns a specific execution string"""
    if val == 'full-round':
        return FIRST_ROUND_FULL
    elif val == 'immediate-split':
        return NETWORK_SPLIT
    elif val == 'no-final':
        return NO_FINAL
    else:
        raise ArgumentTypeError('{} is not a known execution string'.format(val))


FIRST_ROUND_FULL = "M-0-A M-1-B M-2-C M-3-D M-4-E \
                    SJ-1-A SJ-2-A SJ-3-A SJ-4-A SJ-0-B SJ-2-B SJ-3-B SJ-4-B SJ-0-C SJ-1-C \
                    SJ-3-C SJ-4-C SJ-0-D SJ-1-D SJ-2-D SJ-4-D SJ-0-E SJ-1-E SJ-2-E SJ-3-E"

NETWORK_SPLIT = "M-0-R0 SJ-1-R0 M-1-R1 SJ-0-R1 M-0-R2 S-1-R2 M-1-R3 S-0-R3 M-0-R4 S-1-R4 \
                M-3-L0 SJ-4-L0 M-4-L1 SJ-3-L1 M-3-L2 S-4-L2 M-4-L3 S-3-L3 M-3-L4 S-4-L4"


NO_FINAL = "M-1-A M-2-B SJ-2-A SJ-3-B M-2-C M-3-D SJ-3-C SJ-4-D M-3-E M-4-F SJ-4-E SJ-1-F M-4-G M-1-H SJ-1-G SJ-2-H \
            M-1-A1 M-2-B1 SJ-2-A1 SJ-3-B1 M-2-C1 M-3-D1 SJ-3-C1 SJ-4-D1 M-3-E1 M-4-F1 SJ-4-E1 SJ-1-F1 M-4-G1 M-1-H1 SJ-1-G1 SJ-2-H1 \
            M-1-A2 M-2-B2 SJ-2-A2 SJ-3-B2 M-2-C2 M-3-D2 SJ-3-C2 SJ-4-D2 M-3-E2 M-4-F2 SJ-4-E2 SJ-1-F2 M-4-G2 M-1-H2 SJ-1-G2 SJ-2-H2 \
            M-2-A3 SJ-3-A3 M-3-A4 SJ-4-A4 M-4-A5"
