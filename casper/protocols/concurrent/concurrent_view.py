"""The concurrent view module extends a view for concurrent data structures """
import random as r

from casper.abstract_view import AbstractView
import casper.protocols.concurrent.forkchoice as forkchoice


class ConcurrentView(AbstractView):
    """A view class that also keeps track of a last_finalized_estimate and children"""
    def __init__(self, messages=None):
        if not messages:
            messages = set()

        self.children = dict()
        self.last_finalized_estimate = messages

        self.select_outputs = None
        self.create_outputs = None

        super().__init__(messages)

    def set_rewrite_rules(self, select, create):
        self.select_outputs = select
        self.create_outputs = create

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
