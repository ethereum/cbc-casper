from casper.validator import Validator


class ValidatorSet:
    def __init__(self, weights):
        self.validators = {Validator(name, weights[name]) for name in weights}

    def __len__(self):
        return len(self.validators)

    def __iter__(self):
        return iter(self.validators)

    def __contains__(self, v):
        return v in self.validators

    def weight(self, validator_names=None):
        if validator_names is None:
            validators = self.validators
        else:
            validators = self.get_validators_by_names(validator_names)

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
