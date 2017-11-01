import pytest

from casper.abstract_view import AbstractView


def test_new_view():
    view = AbstractView()

    assert not view.messages
    assert not view.latest_messages
    assert not view.justification().latest_messages


@pytest.mark.parametrize(
    'latest_messages',
    [
        ({"face": 10}),
        ({1: 10, 2: 30}),
    ]
)
def test_justification(latest_messages):
    view = AbstractView()
    view.latest_messages = latest_messages

    assert view.justification().latest_messages == latest_messages
