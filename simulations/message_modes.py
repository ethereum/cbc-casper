"""The simulution utils module ... """
import random

class MessageMode(object):
    def get_message_makers(self, validator_set):
        """Returns the validators that should make new messages
        Must be implemented by child class"""
        raise NotImplementedError

    def get_message_recievers(self, validator_set):
        """Returns the validators that should recieve the new messages
        Must be implemented by child class"""
        raise NotImplementedError


class RandomMessageMode(MessageMode):
    def get_message_makers(self, validator_set):
        return random.sample(validator_set.validators, 1)

    def get_message_recievers(self, validator_set):
        return validator_set

class RoundRobinMessageMode(MessageMode):
    current_validator = 0
    def get_message_makers(self, validator_set):
        self.current_validator = (self.current_validator + 1) % len(validator_set)
        return [validator_set.get_validator_by_name(self.current_validator)]

    def get_message_recievers(self, validator_set):
        return validator_set


class FullMessageMode(MessageMode):
    def get_message_makers(self, validator_set):
        return validator_set.validators

    def get_message_recievers(self, validator_set):
        return validator_set


class NoFinalMessageMode(MessageMode):
    # TODO: fix this...
    current_validator = 0
    def get_message_makers(self, validator_set):
        self.current_validator = (self.current_validator + 1) % len(validator_set)
        second_validator = (self.current_validator + 3) % len(validator_set)
        return [
            validator_set.get_validator_by_name(self.current_validator),
            validator_set.get_validator_by_name(second_validator)
            ]

    def get_message_recievers(self, validator_set):
        return validator_set
