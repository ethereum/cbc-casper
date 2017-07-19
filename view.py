from block import Block
from justification import Justification
from settings import NUM_VALIDATORS, VALIDATOR_NAMES, ESTIMATE_SPACE, WEIGHTS
import forkchoice
import copy


class View:
    def __init__(self, messages=set()):

        # now for some assignment...
        self.messages = set()
        self.latest_messages = dict()
        self.children = dict()
        self.last_finalized_block = None

        self.add_messages(messages)

    def __str__(self):
        s = "View: \n"
        for b in self.messages:
            s += str(b) + "\n"
        return s

    # The estimator function returns the set of max weight estimates
    # This may not be a single-element set because the validator may have an empty view
    def estimate(self):
        return forkchoice.get_fork_choice(self.last_finalized_block, copy.copy(self.children), copy.copy(self.latest_messages))

    def justification(self):
        return Justification(self.last_finalized_block, self.latest_messages, self.children)

    # This method updates a validator's observed latest messages (and vicarious latest messages) in response to seeing new messages
    def add_messages(self, showed_messages):

        if len(showed_messages) == 0:
            return

        '''
        PART -1 - type check
        '''

#        for b in showed_messages:
#            assert isinstance(b, Block), "expected only to add messages"

        '''
        PART 0 - finding newly discovered messages
        '''

        newly_discovered_messages = self.get_new_messages(showed_messages)

        '''
        PART 1 - updating the set of viewed messages
        '''

        for b in newly_discovered_messages:
            self.messages.add(b)

        '''
        PART 2 - updating latest messages
        '''

        # updating latest messages..
        for b in newly_discovered_messages:
            if b.sender not in self.latest_messages:
                self.latest_messages[b.sender] = b
                continue
            if self.latest_messages[b.sender].sequence_number < b.sequence_number:
                self.latest_messages[b.sender] = b
                continue
#            assert (b == self.latest_messages[b.sender] or
#                    b.is_dependency_from_same_validator(self.latest_messages[b.sender])), "...did not expect any equivocating nodes!"

        '''
        PART 3 - updating children
        '''
        for b in newly_discovered_messages:
            if b.estimate not in self.children:
                self.children[b.estimate] = set()
            self.children[b.estimate].add(b)

    # This method returns the set of messages out of showed_messages and their dependency that isn't part of the view
    def get_new_messages(self, showed_messages):

        new_messages = set()
        # The memo will keep track of messages we've already looked at, so we don't redo work.
        memo = set()

        # At the start, our working set will be the "showed messages" parameter
        current_set = set(showed_messages)
        while(current_set != set()):

            next_set = set()
            # If there's no message in the current working set
            for message in current_set:

                # Which we haven't seen it in the view or during this loop
                if message not in self.messages and message not in memo:

                    # But if we do have a new message, then we add it to our pile..
                    new_messages.add(message)

                    # and add the best in its justification to our next working set
                    for b in message.justification.latest_messages.values():
                        next_set.add(b)
                # Keeping a record of very message we inspect, being sure not to do any extra (exponential complexity) work
                memo.add(message)

            current_set = next_set

        # After the loop is done, we return a set of new messages
        return new_messages
