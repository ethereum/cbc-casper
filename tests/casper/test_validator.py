"""The validator testing module ... """
import pytest

from casper.validator import Validator


@pytest.mark.parametrize(
    'name, weight, error',
    [
        (1, 10.2, None),
        ("Jim", 5, None),
        (2, 0, None),
        (3, -12, ValueError),
        (None, 13, ValueError),
        (10, None, ValueError),
        (10, 'weightstring', ValueError),
    ]
)
def test_new_validator(name, weight, error, view, message):
    if isinstance(error, type) and issubclass(error, Exception):
        with pytest.raises(error):
            Validator(name, weight, None, view, message)
        return

    validator = Validator(name, weight, None, view, message)
    assert validator.name == name
    assert validator.weight == weight


def test_validator_not_created_with_view(view, message):
    validator = Validator(0, 1, None, view, message)
    assert validator.view == None


def test_validator_saves_initial_message(view, message):
    validator = Validator(0, 1, None, view, message)
    validator.initialize_view(set())
    assert validator.view != None
