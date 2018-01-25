"""The concurrent view module extends a view for concurrent data structures """
import random as r

from casper.abstract_view import AbstractView
import casper.protocols.concurrent.forkchoice as forkchoice


class ConcurrentView(AbstractView):
    """A view class that also keeps track of a last_finalized_estimate and children"""
    def __init__(self, messages=None, genesis_block=None):
        self.children = dict()
        self.last_finalized_estimate = set([genesis_block])
        self.genesis_block = genesis_block

        self._initialize_message_caches(messages)

        # In the future, can change this to any function that follows the interface
        self.select_outputs = self.select_random_outputs_to_consume
        self.create_outputs = self.create_random_new_outputs

        super().__init__(messages)

    def estimate(self):
        """Returns the current forkchoice in this view"""
        available_outputs, output_sources = forkchoice.get_fork_choice(
            self.last_finalized_estimate,
            self.children,
            self.latest_messages
        )

        old_outputs = self.select_outputs(available_outputs, output_sources)
        new_outputs = self.create_outputs(old_outputs, len(old_outputs))
        blocks = {output_sources[output] for output in old_outputs}

        return {'blocks': blocks, 'inputs': old_outputs, 'outputs': new_outputs}

    def select_random_outputs_to_consume(self, available_outputs, output_sources):
        num_outputs = r.randint(1, len(available_outputs))
        return set(r.sample(available_outputs, num_outputs))

    def create_random_new_outputs(self, old_outputs, num_new_outputs):
        return set([r.randint(0, 1000000000) for _ in range(num_new_outputs)])

    def update_safe_estimates(self, validator_set):
        """Checks safety on messages in views forkchoice, and updates last_finalized_estimate"""
        pass

    def _update_protocol_specific_view(self, message):
        """Given a now justified message, updates children and when_recieved"""
        assert message.hash in self.justified_messages, "...should not have seen message!"

        # update the children dictonary with the new message
        for ancestor in message.estimate['blocks']:
            if ancestor not in self.children:
                self.children[ancestor] = set()
            self.children[ancestor].add(message)

        self._update_when_added_cache(message)

    def _initialize_message_caches(self, messages):
        self.when_added = {message: 0 for message in messages}
        self.when_finalized = {self.genesis_block: 0}

    def _update_when_added_cache(self, message):
        if message not in self.when_added:
            self.when_added[message] = len(self.justified_messages)

    def _update_when_finalized_cache(self, tip):
        while tip and tip not in self.when_finalized:
            self.when_finalized[tip] = len(self.justified_messages)
            tip = tip.estimate
