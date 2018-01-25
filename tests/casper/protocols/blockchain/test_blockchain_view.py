"""The BlockchainView testing module..."""
import pytest

@pytest.mark.parametrize(
    'test_string, children',
    [
        (
            "M0-A S1-A M1-B S0-B",
            {'A': ['B']}
        ),
        (
            "M0-A S1-A S2-A S3-A S4-A M1-B M2-C M3-D M4-E S0-B S0-C S0-D S0-E",
            {'A': ['B', 'C', 'D', 'E']}
        ),
        (
            "M0-A S1-A S2-A M1-B M2-C S0-B S0-C M0-D",
            {'A': ['B', 'C'], 'B': ['D']}
        ),
    ]
)
def test_update_protocol_specific_view(test_string, children, blockchain_lang):
    blockchain_lang.parse(test_string)

    validator = blockchain_lang.validator_set.get_validator_by_name(0)

    for block_name in children:
        block = blockchain_lang.messages[block_name]

        for child_name in children[block_name]:
            assert blockchain_lang.messages[child_name] in validator.view.children[block]
