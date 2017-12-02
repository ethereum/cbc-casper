"""The blockchain view module extends a view for blockchain data structures """
from casper.safety_oracles.clique_oracle import CliqueOracle
from casper.abstract_view import AbstractView
from casper.protocols.blockchain.block import Block
import casper.protocols.blockchain.forkchoice as forkchoice


class BlockchainView(AbstractView):
    """A view class that also keeps track of a last_finalized_block and children"""
    def __init__(self, messages=None):
        super().__init__(messages)

        self.children = dict()
        self.last_finalized_block = None

        # cache info about message events
        self.when_added = {}
        for message in self.messages:
            self.when_added[message] = 0
        self.when_finalized = {}

    def estimate(self):
        """Returns the current forkchoice in this view"""
        return forkchoice.get_fork_choice(
            self.last_finalized_block,
            self.children,
            self.latest_messages
        )

    def add_messages(self, showed_messages):
        """Updates views latest_messages and children based on new messages"""

        if not showed_messages:
            return

        for message in showed_messages:
            assert isinstance(message, Block), "expected only to add a block!"

        # find any not-seen messages
        newly_discovered_messages = self.get_new_messages(showed_messages)

        # add these new messages to the messages in view
        self.messages.update(newly_discovered_messages)

        for message in newly_discovered_messages:
            # update views most recently seen messages
            if message.sender not in self.latest_messages:
                self.latest_messages[message.sender] = message
            elif self.latest_messages[message.sender].sequence_number < message.sequence_number:
                self.latest_messages[message.sender] = message

            # update the children dictonary with the new message
            if message.estimate not in self.children:
                self.children[message.estimate] = set()
            self.children[message.estimate].add(message)

            # update when_added cache
            if message not in self.when_added:
                self.when_added[message] = len(self.messages)

    def make_new_message(self, validator):
        justification = self.justification()
        estimate = self.estimate()

        new_message = Block(estimate, justification, validator)
        self.add_messages(set([new_message]))

        return new_message

    def update_safe_estimates(self, validator_set):
        """Checks safety on messages in views forkchoice, and updates last_finalized_block"""
        tip = self.estimate()

        prev_last_finalized_block = self.last_finalized_block

        while tip and tip != prev_last_finalized_block:
            oracle = CliqueOracle(tip, self, validator_set)
            fault_tolerance, _ = oracle.check_estimate_safety()

            if fault_tolerance > 0:
                self.last_finalized_block = tip
                # then, a sanity check!
                if prev_last_finalized_block:
                    assert prev_last_finalized_block.is_in_blockchain(self.last_finalized_block)

                # cache when_finalized
                while tip and tip not in self.when_finalized:
                    self.when_finalized[tip] = len(self.messages)
                    tip = tip.estimate

                return self.last_finalized_block

            tip = tip.estimate
