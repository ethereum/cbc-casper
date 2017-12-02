import pytest

from casper.protocols.binary.binary_view import BinaryView


def test_init():
    view = BinaryView(None)
    assert view.minimum == 0
    assert view.maximum == 1


def test_cannot_override_min_max():
    with pytest.raises(TypeError):
        BinaryView(None, 10, 500)
