"""The validator set module ... """
from casper.validator import Validator


class ValidatorSet:
    """Defines the validator set."""
    def __init__(self, weights):
        self.validators = {Validator(name, weights[name], self) for name in weights}

    def __len__(self):
        return len(self.validators)

    def __iter__(self):
        return iter(self.validators)

    def __contains__(self, validator):
        return validator in self.validators

    def weight(self, validators=None):
        if validators is None:
            validators = self.validators

        return sum(map(lambda v: v.weight, validators))

    def sorted_by_name(self):
        return sorted(list(self.validators), key=lambda v: v.name)

    def get_validator_by_name(self, name):
        return self.get_validators_by_names([name]).pop()

    def get_validators_by_names(self, names):
        return set(filter(lambda v: v.name in names, self.validators))

    def validator_names(self):
        return set(map(lambda v: v.name, self.validators))

    def validator_weights(self):
        return set(map(lambda v: v.weight, self.validators))
