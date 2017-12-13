from utils.clock import Clock


class ValidatorClient(Clock):
    """Validator client software that makes decisions about when
    to make and send new messages"""
    def __init__(self, validator, network):
        super().__init__()
        self.validator = validator
        self.network = network

    def should_make_new_message(self):
        pass

    def make_new_message(self):
        if self.should_make_new_message():
            return self.validator.make_new_message()

    def retrieve_messages(self):
        messages = self.network.receive_all_available(self.validator)
        self.validator.receive_messages(set(messages))
        return messages

    def propagate_message(self, message):
        """ could change this out to send to only peers """
        self.network.send_to_all(message)

    def make_and_propagate_message(self):
        message = self.make_new_message()
        if message:
            self.propagate_message(message)
        return message
