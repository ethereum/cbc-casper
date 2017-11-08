"""The justification module ..."""


class Justification(object):
    """The justification class ..."""
    def __init__(self, latest_messages=None):
        if latest_messages is None:
            latest_messages = {}
        self.latest_messages = dict()
        for validator in latest_messages:
            self.latest_messages[validator] = latest_messages[validator].header
