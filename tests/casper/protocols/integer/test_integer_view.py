import pytest

from casper.protocols.integer.integer_view import IntegerView


@pytest.mark.parametrize(
    'minimum, maximum, error',
    [
        (0, 100, None),
        (400, 450, None),
        (299, 300, None),
        (300, 300, None),
        (100, 50, ValueError),
        (299, 288, ValueError),
    ]
)
def test_set_min_and_max(minimum, maximum, error):
    if isinstance(error, type) and issubclass(error, Exception):
        with pytest.raises(error):
            IntegerView(None, minimum, maximum)
        return

    view = IntegerView(None, minimum, maximum)
    assert view.minimum == minimum
    assert view.maximum == maximum
