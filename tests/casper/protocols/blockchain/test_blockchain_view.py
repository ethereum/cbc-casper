"""The BlockchainView testing module..."""
import pytest

@pytest.mark.parametrize(
    'test_string, children',
    [
        (
            "M-0-A S-1-A M-1-B S-0-B",
            {'A': ['B']}
        ),
        (
            "M-0-A S-1-A S-2-A S-3-A S-4-A M-1-B M-2-C M-3-D M-4-E S-0-B S-0-C S-0-D S-0-E",
            {'A': ['B', 'C', 'D', 'E']}
        ),
        (
            "M-0-A S-1-A S-2-A M-1-B M-2-C S-0-B S-0-C M-0-D",
            {'A': ['B', 'C'], 'B': ['D']}
        ),
    ]
)
def test_update_protocol_specific_view(test_string, children, blockchain_instantiated):
    blockchain_instantiated.execute(test_string)

    validator = blockchain_instantiated.global_validator_set.get_validator_by_name(0)

    for block_name in children:
        block = blockchain_instantiated.messages[block_name]

        for child_name in children[block_name]:
            assert blockchain_instantiated.messages[child_name] in validator.view.children[block]
