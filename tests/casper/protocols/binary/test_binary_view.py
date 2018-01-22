import pytest


@pytest.mark.skip(reason="inital messages not yet specified")
def test_update_safe_estimates(weights, test_string, finalized, binary_lang_creator):
    binary_lang = binary_lang_creator(weights)
    binary_lang.parse(test_string)

    validator = binary_lang.validator_set.get_validator_by_name(0)

    validator.view.update_safe_estimates(binary_lang.validator_set)

    assert validator.view.last_finalized_estimate.estimate == finalized







@pytest.mark.skip(reason="test language not written")
def test_update_protocol_specific_view():
    pass
