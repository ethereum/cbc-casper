"""The justification module ..."""
class Justification:
    """The justification class ..."""
    def __init__(self, latest_messages=None):
        self.latest_messages = dict()
        if latest_messages:
            for validator in latest_messages:
                self.latest_messages[validator] = latest_messages[validator]
