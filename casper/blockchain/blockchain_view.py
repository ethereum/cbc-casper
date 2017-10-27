"""The view module ... """
from casper.justification import Justification
from casper.safety_oracles.clique_oracle import CliqueOracle
from casper.abstract_view import AbstractView
from casper.blockchain.block import Block
import casper.forkchoice as forkchoice


class BlockchainView(AbstractView):
    """A set of seen messages. For performance, also stores a dict of most recent messages."""
    def __init__(self, messages=set()):
        super().__init__(messages)

        self.children = dict()
        self.last_finalized_block = None


    def estimate(self):
        """The estimate function returns the set of max weight estimates
        This may not be a single-element set because the validator may have an empty view."""
        return forkchoice.get_fork_choice(
            self.last_finalized_block,
            self.children,
            self.latest_messages
        )

    def add_messages(self, showed_messages):
        """This method updates a validator's observed latest messages
        (and vicarious latest messages) in response to seeing new messages."""

        if not showed_messages:
            return

        #### PART -1 - type check

        for message in showed_messages:
            assert isinstance(message, Block), "expected only to add a block!"

        #### PART 0 - finding newly discovered messages

        newly_discovered_messages = self.get_new_messages(showed_messages)

        #### PART 1 - updating the set of viewed messages

        self.messages.update(newly_discovered_messages)

        #### PART 2 - updating latest messages

        # Updating latest messages...
        for bet in newly_discovered_messages:
            if bet.sender not in self.latest_messages:
                self.latest_messages[bet.sender] = bet
                continue
            if self.latest_messages[bet.sender].sequence_number < bet.sequence_number:
                self.latest_messages[bet.sender] = bet
                continue

        #### PART 3 - updating children

        for bet in newly_discovered_messages:
            if bet.estimate not in self.children:
                self.children[bet.estimate] = set()
            self.children[bet.estimate].add(bet)


    def update_safe_estimates(self, validator_set):
        tip = self.estimate()

        prev_last_finalized_block = self.last_finalized_block

        while tip and tip != prev_last_finalized_block:
            oracle = CliqueOracle(tip, self, validator_set)
            fault_tolerance, num_node_ft = oracle.check_estimate_safety()

            if fault_tolerance > 0:
                self.last_finalized_block = tip
                if prev_last_finalized_block:
                    assert prev_last_finalized_block.is_in_blockchain(self.last_finalized_block)

                return

            tip = tip.estimate
