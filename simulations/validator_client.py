class ValidatorClient(object):
    """Validator client software that makes decisions about when
    to make and send new messages"""
    def __init__(self, validator):
        self.validator = validator

    def should_make_new_message(self):
        pass

    def make_new_message(self):
        if self.should_make_new_message():
            return self.validator.make_new_message()
