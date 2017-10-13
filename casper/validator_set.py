from casper.validator import Validator


class ValidatorSet:
    def __init__(self, weights):
        self.validators = {Validator(name, weights[name]) for name in weights}

    def weight(self, validator_names=None):
        if validator_names is None:
            validators = self.validators
        else:
            validators = self.get_validators_by_name(validator_names)

        return sum(map(lambda v: v.weight, validators))

    def get_validators_by_name(self, names):
        return set(filter(lambda v: v.name in names, self.validators))

    def validator_names(self):
        return set(map(lambda v: v.name, self.validators))
