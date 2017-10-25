"""The justification module ..."""
class Justification:
    """The justification class ..."""
    def __init__(self, last_finalized_block=None, latest_messages=dict()):
        self.last_finalized_block = last_finalized_block
        self.latest_messages = dict()
        for validator in latest_messages:
            self.latest_messages[validator] = latest_messages[validator]
