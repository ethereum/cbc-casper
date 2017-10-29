"""The BlockchainView testing module..."""
import pytest

from casper.blockchain.blockchain_view import BlockchainView
from casper.testing_language import TestLangCBC


@pytest.mark.parametrize(
    'weights, test_string, showed_message_names, new_message_names',
    [
        (
            {0: 10, 1: 11},
            "B0-A S1-A B1-B S0-B B0-C S1-C B1-D S0-D",
            ["C", "D"],
            ["A", "B", "C", "D"]
        ),
        (
            {0: 10, 1: 11},
            "B0-A S1-A B1-B S0-B B0-C S1-C B1-D S0-D",
            ["C"],
            ["A", "B", "C"]
        ),
        (
            {0: 10, 1: 11, 2: 30},
            "B0-A S1-A B1-B S0-B B0-C S1-C B2-D S0-D S1-D",
            ["D"],
            ["D"]
        ),
        (
            {0: 10, 1: 11, 2: 500},
            "B0-A S1-A B1-B S0-B B0-C S2-C B2-D S0-D S1-D",
            ["D"],
            ["A", "B", "C", "D"]
        ),
    ]
)
def test_get_new_messages(weights, test_string, showed_message_names, new_message_names, report):
    test_lang = TestLangCBC(weights, BlockchainView, report)

    view = BlockchainView()
    # add the initial messages to the view
    view.add_messages(test_lang.network.global_view.messages)
    test_lang.parse(test_string)

    showed_messages = {test_lang.blocks[name] for name in showed_message_names}
    new_messages = {test_lang.blocks[name] for name in new_message_names}

    assert view.get_new_messages(showed_messages) == new_messages
