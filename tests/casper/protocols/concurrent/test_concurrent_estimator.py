"""The forkchoice testing module ... """
import pytest
import random as r

from casper.protocols.concurrent.concurrent_protocol import ConcurrentProtocol
import casper.protocols.concurrent.forkchoice as forkchoice

from simulations.json_generator import generate_concurrent_json

# TODO: Test once there is a complete concurrent testing language


def test_gets_correct_sources():
    json = generate_concurrent_json(exe_str='',
        start_out=[0, 100, 200],
        gen_est=[0, 100],
        select_outputs='all',
        create_outputs='all',
    )
    protocol = ConcurrentProtocol(json, False, False, 1)
    available_outputs, output_sources = forkchoice.get_fork_choice(
        protocol.global_view.children,
        protocol.global_view.latest_messages
    )
    #TODO
