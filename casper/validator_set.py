"""The validator set module contains the ValidatorSet class """
from casper.validator import Validator
from casper.blockchain.blockchain_protocol import BlockchainProtocol


class ValidatorSet:
    """Defines the validator set."""
    def __init__(self, weights, protocol=BlockchainProtocol):
        if protocol == BlockchainProtocol:
            self.genesis_block = self._make_genesis_block()
            self.validators = {
                Validator(name, weights[name], protocol, self, self.genesis_block)
                for name in weights
            }
        else:
            self.validators = {Validator(name, weights[name], protocol, self) for name in weights}

    def _make_genesis_block(self):
        genesis_block = BlockchainProtocol.Message(
            None,
            dict(),
            None,
            0,
            -1
        )
        return genesis_block

    def __len__(self):
        return len(self.validators)

    def __iter__(self):
        return iter(self.validators)

    def __contains__(self, validator):
        return validator in self.validators

    def weight(self, validators=None):
        """Returns the weight of the passed valdiator set, else the sum of all validators weight"""
        if validators is None:
            validators = self.validators

        return sum(v.weight for v in validators)

    def sorted_by_name(self):
        """Returns a list of validators sorted by their name"""
        return sorted(list(self.validators), key=lambda v: v.name)

    def sorted_by_weight(self):
        """Returns a list of validators sorted by their weight"""
        return sorted(list(self.validators), key=lambda v: v.weight)

    def get_validator_by_name(self, name):
        """Returns the validator with a given name"""
        return self.get_validators_by_names([name]).pop()

    def get_validators_by_names(self, names):
        """Returns the set of validators with the passed names"""
        return {v for v in self.validators if v.name in names}

    def validator_names(self):
        """Returns the set of all validators names"""
        return {v.name for v in self.validators}

    def validator_weights(self):
        """Returns the set of all validator weights"""
        return {v.weight for v in self.validators}
