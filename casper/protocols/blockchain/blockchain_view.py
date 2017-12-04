"""The blockchain view module extends a view for blockchain data structures """
import queue as Q
import copy

from casper.safety_oracles.clique_oracle import CliqueOracle
from casper.abstract_view import AbstractView
from casper.protocols.blockchain.block import Block
import casper.protocols.blockchain.forkchoice as forkchoice
import casper.utils as utils


class BlockchainView(AbstractView):
    """A view class that also keeps track of a last_finalized_block and children"""
    def __init__(self, messages=None):
        super().__init__(messages)

        self.children = dict()
        self.minimal_children = {None: set()}
        self.last_finalized_block = None

        # cache info about message events
        self.when_added = {}
        for message in self.messages:
            self.when_added[message] = 0
        self.when_finalized = {}

    def estimate(self):
        """Returns the current forkchoice in this view"""
        regular_forkchoice = forkchoice.get_fork_choice(
            self.last_finalized_block,
            self.children,
            self.latest_messages
        )

        minimal_forkchoice = forkchoice.get_fork_choice(
            self.last_finalized_block,
            self.minimal_children,
            self.latest_messages
        )
        if regular_forkchoice != minimal_forkchoice:
            assert False

        return regular_forkchoice


    def reduce_tree(self, root, latest_messages, children):
        new_children = dict()
        to_reduce = Q.Queue()

        to_reduce.put(root)

        while not to_reduce.empty():
            current_message = to_reduce.get()
            assert current_message not in new_children
            new_children[current_message] = set()

            if current_message not in children:
                continue

            for child in children[current_message]:
                critical_descendant = self.get_first_critical_descendant(
                    child,
                    latest_messages,
                    children
                )

                if critical_descendant:
                    new_children[current_message].add(critical_descendant)
                    to_reduce.put(critical_descendant)

        self.update_children(root, children, new_children)


    def update_children(self, root, children, new_children):
        assert root in new_children
        self.delete_subtree(root, children)

        for message in new_children:
            assert message not in children
            if not any(new_children[message]):
                continue
            children[message] = new_children[message]


    def delete_subtree(self, root, children):
        if root not in children:
            return

        for child in children[root]:
            self.delete_subtree(child, children)

        del children[root]


    def get_first_critical_descendant(self, message, latest_messages, children):
        if message in latest_messages.values():
            return message
        if self.is_stressed_ancestor(message, latest_messages, children):
            return message

        if message not in children:
            return None

        critical_children = set()
        for child in children[message]:
            critical_children.add(
                self.get_first_critical_descendant(
                    child, latest_messages, children
                )
            )

        if not any(critical_children):
            return None
        if len(critical_children) == 1:
            return critical_children.pop()
        if len(critical_children) == 2:
            assert None in critical_children # otherwise, should be considered a stressed ancestor
            critical_children.remove(None)
            return critical_children.pop()

        raise Exception(
            "Something is wrong! To many critical children: {}".format(critical_children)
        )

    def is_stressed_ancestor(self, message, latest_messages, children):
        if message not in children or len(children[message]) <= 1:
            return False

        num_children_with_lm = 0
        for child in children[message]:
            if self.get_num_latest_message_descendants(child, latest_messages) > 0:
                num_children_with_lm += 1
                if num_children_with_lm >= 2:
                    return True

        return False

    def get_num_latest_message_descendants(self, root, latest_messages):
        num_lm_descendants = 0
        for message in latest_messages.values():
            if root.is_in_blockchain(message):
                num_lm_descendants += 1

        return num_lm_descendants


    def add_messages(self, showed_messages):
        """Updates views latest_messages and children based on new messages"""

        if not showed_messages:
            return

        for message in showed_messages:
            assert isinstance(message, Block), "expected only to add a block!"

        # find any not-seen messages
        newly_discovered_messages = self.get_new_messages(showed_messages)

        for message in newly_discovered_messages:
            # update views most recently seen messages
            if message.sender not in self.latest_messages:
                self.latest_messages[message.sender] = message
            elif self.latest_messages[message.sender].sequence_number < message.sequence_number:
                self.latest_messages[message.sender] = message

            # update when_added cache
            if message not in self.when_added:
                self.when_added[message] = len(self.messages)

        self.add_to_children(newly_discovered_messages)

        # add these new messages to the messages in view
        self.messages.update(newly_discovered_messages)


    def add_to_children(self, new_messages):
        oldest_messages = {
            message for message in new_messages
            if message.estimate not in new_messages
        }

        while any(oldest_messages):
            for message in oldest_messages:
                assert message not in self.messages
                assert message.estimate not in oldest_messages and message.estimate not in new_messages
                self.update_minimal_tree(message, self.latest_messages, self.minimal_children)
                if message.estimate not in self.children:
                    self.children[message.estimate] = set()
                self.children[message.estimate].add(message)

            new_messages.difference_update(oldest_messages)
            oldest_messages = {
                message for message in new_messages
                if message.estimate not in new_messages
            }


    def update_minimal_tree(self, new_message, latest_messages, minimal_children):
        root = self.get_youngest_ancestor_in_tree(new_message, minimal_children)
        assert root != new_message
        assert root in minimal_children

        added = False
        for child in minimal_children[root]:
            if new_message == child or added:
                # we have already seen this message and added it!
                return
            common_ancestor = self.get_common_ancestor(child, new_message)

            if common_ancestor == child:
                added = True
                assert child.is_in_blockchain(new_message)
                assert child not in minimal_children
                minimal_children[child] = set()
                minimal_children[child].add(new_message)

            elif common_ancestor != root:
                added = True
                minimal_children[root].remove(child)
                minimal_children[root].add(common_ancestor)
                minimal_children[common_ancestor] = set()
                minimal_children[common_ancestor].add(new_message)
                minimal_children[common_ancestor].add(child)

        if not added:
            minimal_children[root].add(new_message)

        if new_message.sender not in new_message.justification.latest_messages:
            # there is no previous message, and so we don't need to update the tree!
            # NOTE: I'm not actually sure this is the case :)
            return

        last_message = new_message.justification.latest_messages[new_message.sender]
        common_ancestor = self.get_common_ancestor(new_message, last_message)

        # old message should be removed from tree during this function call, sometimes (there are cases where it is not)!
        self.reduce_tree(common_ancestor, latest_messages, minimal_children)


    def get_youngest_ancestor_in_tree(self, message, minimal_children):
        """Returns None if no ancestor in tree"""
        curr_message = message
        while curr_message and curr_message not in minimal_children:
            curr_message = curr_message.estimate

        return curr_message


    def get_common_ancestor(self, message_one, message_two):
        if message_one == message_two:
            return message_one

        if message_one.height < message_two.height:
            message_two = self.estimate_at_height(message_two, message_one.height)
        else:
            message_one = self.estimate_at_height(message_one, message_two.height)

        while message_one:
            if message_one == message_two:
                return message_one
            message_one = message_one.estimate
            message_two = message_two.estimate


        return None

    def estimate_at_height(self, message, height):
        assert height <= message.height and height >= 0

        while message.height != height:
            message = message.estimate

        return message



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
