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


class NoFinalMessageMode(RoundRobinMessageMode):
    def get_message_makers(self, validator_set):
        val_one = super().get_message_makers(validator_set)[0]
        val_two = super().get_message_makers(validator_set)[0]
        return [val_one, val_two]
