"""The language testing module ... """
import pytest

from testing_languages.binary_test_lang import BinaryTestLang
from casper.network import Network
from casper.validator_set import ValidatorSet


def test_init_creates_state_lang(test_weight):
    binary_lang = BinaryTestLang(test_weight, False)

    binary_lang.messages
    binary_lang.plot_tool

    assert isinstance(binary_lang.network, Network)
    assert isinstance(binary_lang.validator_set, ValidatorSet)

    assert len(binary_lang.validator_set) == len(test_weight)

    # should only have seen their initial message
    for validator in binary_lang.validator_set:
        assert len(validator.view.justified_messages) == 1


@pytest.mark.parametrize(
    'test_string, error',
    [
        ('CE0-2', AssertionError),
        ('CS0-2', AssertionError),
        ('CU0-2', AssertionError),
        ('CE0-A', ValueError),
        ('CS0-A', ValueError),
        ('CU0-A', ValueError),
    ]
)
def test_only_binary_estimates(test_string, error, binary_lang):
    binary_lang.parse('M0-A')

    with pytest.raises(error):
        binary_lang.parse(test_string)


def test_check_estimate_passes_on_valid_assertions(binary_lang):
    binary_lang.parse('M0-A S1-A S2-A S3-A S4-A')

    current_estimates = dict()
    for validator in binary_lang.validator_set:
        current_estimates[validator] = validator.estimate()

    check_estimate = ''
    for validator in binary_lang.validator_set:
        check_estimate += 'CE' + str(validator.name) + '-' + str(current_estimates[validator]) + ' '
    check_estimate = check_estimate[:-1]

    binary_lang.parse(check_estimate)


@pytest.mark.parametrize(
    'test_string',
    [
        ('M0-A CE0-0 CE0-1'),
        ('RR0-A RR0-B CE0-0 CE0-1'),
        ('M0-A CS0-0 CS0-1'),
        ('RR0-A RR0-B CS1-0 CS1-1'),
    ]
)
def test_checks_fails_on_invalid_assertions(test_string, binary_lang):
    with pytest.raises(AssertionError):
        binary_lang.parse(test_string)


def test_check_safe_passes_on_valid_assertions(binary_lang):
    binary_lang.parse('RR0-A RR0-B RR0-C RR0-D')

    current_estimate = binary_lang.network.global_view.estimate()

    check_safe = ''
    for validator in binary_lang.validator_set:
        check_safe += 'CS' + str(validator.name) + '-' + str(current_estimate) + ' '
    check_safe = check_safe[:-1]

    binary_lang.parse(check_safe)


def test_check_unsafe_passes_on_valid_assertions(binary_lang):
    binary_lang.parse('M0-A S1-A S2-A S3-A S4-A CU0-0 CU0-1 CU1-0 CU1-1 CU2-0 CU2-1 CU3-0 CU3-1 CU4-0 CU4-1')

    for validator in binary_lang.validator_set:
        assert validator.view.last_finalized_estimate is None


def test_check_unsafe_passes_on_valid_assertions_rr(binary_lang):
    binary_lang.parse('RR0-A RR0-B RR0-C RR0-D')

    current_estimate = binary_lang.network.global_view.estimate()

    check_unsafe = ''
    for validator in binary_lang.validator_set:
        check_unsafe += 'CU' + str(validator.name) + '-' + str(1 - current_estimate) + ' '
    check_unsafe = check_unsafe[:-1]

    binary_lang.parse(check_unsafe)


def test_check_unsafe_fails_on_invalid_assertions(binary_lang):
    binary_lang.parse('RR0-A RR0-B RR0-C RR0-D')

    current_estimate = binary_lang.network.global_view.estimate()

    with pytest.raises(AssertionError):
        binary_lang.parse('CU0-' + str(current_estimate))
