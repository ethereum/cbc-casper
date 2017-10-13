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
def test_new_validator(name, weight, error):
    if isinstance(error, type) and issubclass(error, Exception):
        with pytest.raises(error):
            Validator(name, weight)
        return

    validator = Validator(name, weight)
    assert validator.name == name
    assert validator.weight == weight
