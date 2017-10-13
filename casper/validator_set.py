from casper.validator import Validator


class ValidatorSet:
    def __init__(self, weights):
        self.validators = {Validator(name, weights[name]) for name in weights}

    def weight(self, validators=None):
        if validators is None:
            validators = self.validators