"""The justification module ..."""
class Justification:
    """The justification class ..."""
    def __init__(self, latest_messages=dict()):
        self.latest_messages = dict()
        for validator in latest_messages:
            self.latest_messages[validator] = latest_messages[validator]
