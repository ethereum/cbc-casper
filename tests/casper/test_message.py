def test_message_implements_interface(message):
    assert callable(message.is_valid_estimate)
    assert callable(message.conflicts_with)

    assert message.is_valid_estimate(0) is not None
