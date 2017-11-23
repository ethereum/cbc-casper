"""The blockchain view module extends a view for blockchain data structures """
from casper.safety_oracles.clique_oracle import CliqueOracle
from casper.abstract_view import AbstractView
import casper.blockchain.forkchoice as forkchoice


class BlockchainView(AbstractView):
    """A view class that also keeps track of a last_finalized_block and children"""
    def __init__(self, messages=None):
        super().__init__(messages)

        self.children = dict()
        self.last_finalized_block = None

        self._initialize_message_caches()

    def estimate(self):
        """Returns the current forkchoice in this view"""
        return forkchoice.get_fork_choice(
            self.last_finalized_block,
            self.children,
            self.latest_messages
        )

    def update_safe_estimates(self, validator_set):
        """Checks safety on messages in views forkchoice, and updates last_finalized_block"""
        tip = self.estimate()

        while tip and tip != self.last_finalized_block:
            oracle = CliqueOracle(tip, self, validator_set)
            fault_tolerance, _ = oracle.check_estimate_safety()

            if fault_tolerance > 0:
                self.last_finalized_block = tip
                self._update_when_finalized_cache(tip)
                return self.last_finalized_block

            tip = tip.estimate

    def update_protocol_specific_view(self, message):
        """Given a now justified message, updates children and when_recieved"""
        assert message.hash in self.justified_messages, "...should not have seen message!"

        # update the children dictonary with the new message
        if message.estimate not in self.children:
            self.children[message.estimate] = set()
        self.children[message.estimate].add(message)

        self._update_when_added_cache(message)

    def _initialize_message_caches(self):
        self.when_added = {}
        for message in self.justified_messages.values():
            self.when_added[message] = 0
        self.when_finalized = {}

    def _update_when_added_cache(self, message):
        if message not in self.when_added:
            self.when_added[message] = len(self.justified_messages)

    def _update_when_finalized_cache(self, tip):
        while tip and tip not in self.when_finalized:
            self.when_finalized[tip] = len(self.justified_messages)
            tip = tip.estimate
