"""The justification module ..."""


class Justification:
    """The justification class ..."""
    def __init__(self, last_finalized_block=None, latest_messages=None):
        self.last_finalized_block = last_finalized_block
        self.latest_messages = dict()
        if latest_messages:
            for validator in latest_messages:
                self.latest_messages[validator] = latest_messages[validator]
