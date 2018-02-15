"""The sharding view module extends a view for sharded blockchain data structure"""
import random as r

from casper.safety_oracles.clique_oracle import CliqueOracle
from casper.abstract_view import AbstractView
import casper.protocols.sharding.forkchoice as forkchoice


class ShardingView(AbstractView):
    """A view class that keeps track of children, latest_messages_on_shard and starting_blocks"""
    def __init__(self, messages=None, shard_genesis_block=None):
        self.children = dict()

        self.shard_genesis_blocks = dict()  # shard_id -> genesis for shard
        self.starting_blocks = dict()  # shard_id -> starting block for forkchoice
        self.latest_messages_on_shard = dict()  # shard_id -> validator -> message

        self.select_shards = self.select_random_shards

        if shard_genesis_block:
            for shard_id in shard_genesis_block.estimate['shard_ids']:
                self.shard_genesis_blocks[shard_id] = shard_genesis_block
                self.starting_blocks[shard_id] = shard_genesis_block

        super().__init__(messages)

    def estimate(self):
        """Returns the current forkchoice in this view"""
        shards_forkchoice = dict()

        for shard_id in sorted(self.starting_blocks):
            shard_tip = forkchoice.get_shard_fork_choice(
                self.starting_blocks[shard_id],
                self.children,
                self.latest_messages_on_shard[shard_id],
                shard_id
            )
            shards_forkchoice[shard_id] = shard_tip

            left_child_shard = shard_id + '0'
            right_child_shard = shard_id + '1'
            if left_child_shard in self.starting_blocks:
                self.set_child_starting_block(shard_tip, shard_id, left_child_shard)
            if right_child_shard in self.starting_blocks:
                self.set_child_starting_block(shard_tip, shard_id, right_child_shard)

        self.check_forkchoice_atomicity(shards_forkchoice)

        shards_to_build_on = self.select_shards(shards_forkchoice)
        return {'prev_blocks': {shards_forkchoice[shard_id] for shard_id in shards_to_build_on},
                'shard_ids': shards_to_build_on}

    def set_child_starting_block(self, tip_block, parent_id, child_id):
        """Changes the starting block for the forkchoice of a shard"""
        child_merge_block = self.previous_merge_block_on_shard(
            tip_block,
            parent_id,
            child_id
        )

        if child_merge_block:
            self.starting_blocks[child_id] = child_merge_block
        else:
            self.starting_blocks[child_id] = self.shard_genesis_blocks[child_id]

    def select_random_shards(self, shards_forkchoice):
        """Randomly selects a shard to build on, and sometimes selects another child shard"""
        shards_to_build_on = [r.choice([key for key in self.starting_blocks.keys()])]
        if (r.randint(0, 1) == 1):
            child = str(r.randint(0, 1))
            if shards_to_build_on[0] + child in self.starting_blocks:
                shards_to_build_on.append(shards_to_build_on[0] + child)

        return set(shards_to_build_on)

    def check_forkchoice_atomicity(self, shards_forkchoice):
        """Asserts that if a merge block is in the forkchoice for a parent chain
        then it is in the forkchoice for a child chain"""
        print("Checking merge block atomicity")
        for shard_id in sorted(shards_forkchoice):
            tip = shards_forkchoice[shard_id]

            for child_shard_id in [shard_id + '0', shard_id + '1']:
                if child_shard_id not in shards_forkchoice:
                    continue

                merge_block = self.previous_merge_block_on_shard(
                    tip,
                    shard_id,
                    child_shard_id
                )
                if merge_block:
                    assert merge_block.is_in_blockchain(
                        shards_forkchoice[child_shard_id],
                        child_shard_id
                    )
        print("Passed")

    def previous_merge_block_on_shard(self, starting_block, block_shard_id, merge_shard):
        """Get the most recent merge block between block_shard_id and merge_shard
        Starts from starting_block"""
        assert starting_block.on_shard(block_shard_id)
        current_block = starting_block
        while current_block:
            if current_block.on_shard(merge_shard):
                assert current_block.is_merge_block
                return current_block
            current_block = current_block.prev_block(block_shard_id)
        return None

    def update_safe_estimates(self, validator_set):
        """Checks safety on messages in views forkchoice, and updates last_finalized_block"""
        # check the safety of the top shard!
        pass

        tip = None

        while tip and tip != self.starting_blocks['']:
            oracle = CliqueOracle(tip, self, validator_set)
            fault_tolerance, _ = oracle.check_estimate_safety()

            if fault_tolerance > 0:
                self.starting_blocks[''] = tip
                return tip

            tip = tip.prev_block('')

    def _update_protocol_specific_view(self, message):
        """Given a now justified message, updates children and when_recieved"""
        assert message.hash in self.justified_messages, "...should not have seen message!"

        # set starting messages! ::))
        if None in message.estimate['prev_blocks']:
            for shard_id in message.estimate['shard_ids']:
                self.shard_genesis_blocks[shard_id] = message
                self.starting_blocks[shard_id] = message

        # update the latest_messages
        for shard_id in message.estimate['shard_ids']:
            if shard_id not in self.latest_messages_on_shard:
                self.latest_messages_on_shard[shard_id] = dict()
            latest_messages = self.latest_messages_on_shard[shard_id]
            if message.sender not in latest_messages:
                latest_messages[message.sender] = message
            elif latest_messages[message.sender].sequence_number < message.sequence_number:
                latest_messages[message.sender] = message

        # update children dictonary
        for parent in message.estimate['prev_blocks']:
            if parent not in self.children:
                self.children[parent] = set()
            self.children[parent].add(message)
