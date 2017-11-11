import pytest

from casper.abstract_view import AbstractView


def test_new_view():
    view = AbstractView()

    assert not any(view.justified_messages)
    assert not view.latest_messages
    assert not view.justification().latest_messages


@pytest.mark.skip(reason="test not yet implemented")
def test_justification_stores_header(latest_messages):
    pass

@pytest.mark.skip(reason="test not yet implemented")
def test_add_justified_message():
    pass

@pytest.mark.skip(reason="test not yet implemented")
def test_dont_add_non_justified_message():
    pass

@pytest.mark.skip(reason="test not yet implemented")
def test_resolve_non_justified_message_when_justification_arrives():
    pass
