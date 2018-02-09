"""The blockchain view module extends a view for blockchain data structures """
import random as r

from casper.safety_oracles.clique_oracle import CliqueOracle
from casper.abstract_view import AbstractView
import casper.protocols.sharding.forkchoice as forkchoice


class ShardingView(AbstractView):
    """A view class that also keeps track of a last_finalized_block and children"""
    def __init__(self, messages=None, shard_genesis_block=None):
        self.children = dict()

        self.starting_blocks = dict() # shard_id -> current starting block for the forkchoice
        if shard_genesis_block:
            assert not shard_genesis_block.is_merge_block
            shard_id = r.sample(shard_genesis_block.estimate['shard_ids'], 1)[0]
            self.starting_blocks[shard_id] = shard_genesis_block
        # note: the shard_genesis_block should _not_ be merge mined!

        self.latest_messages_on_shard = dict() # shard_id -> validator -> message

        super().__init__(messages)

    def estimate(self):
        """Returns the current forkchoice in this view"""
        print("\n\n Running Forkchoice")
        self.update_starting_blocks()

        shards_forkchoice = forkchoice.get_all_shards_fork_choice(
            self.starting_blocks,
            self.children,
            self.latest_messages_on_shard
        )

        self.check_forkchoice_atomicity(shards_forkchoice)

        # for now, randomly build somewhere!
        shards_to_build_on = r.choice([{''}, {'0'}, {'1'}, {'', '0'}, {'', '1'}])
        return {'prev_blocks': {shards_forkchoice[shard_id] for shard_id in shards_to_build_on},
                'shard_ids': shards_to_build_on}

    def check_forkchoice_atomicity(self, shards_forkchoice):
        # assert the atomicity things about the shards_forkchoice
        bast_chain_tip = self.forkchoice_on_shard('')
        zero_chain_tip = self.forkchoice_on_shard('0')
        one_chain_tip = self.forkchoice_on_shard('1')

        zero_merge_block = self.previous_merge_block_on_shard(bast_chain_tip, '', '0')
        one_merge_block = self.previous_merge_block_on_shard(bast_chain_tip, '', '1')

        if zero_merge_block:
            assert zero_merge_block.is_in_blockchain(zero_chain_tip, '0')
            print("Checked shard '' and 0 atomicity: passed")
        if one_merge_block:
            assert one_merge_block.is_in_blockchain(one_chain_tip, '1')
            print("Checked shard '' and 1 atomicity: passed")


    def previous_merge_block_on_shard(self, starting_block, block_shard_id, merge_shard):
        assert starting_block.on_shard(block_shard_id)
        current_block = starting_block
        while current_block:
            if current_block.on_shard(merge_shard):
                assert current_block.is_merge_block
                return current_block
            current_block = current_block.prev_block(block_shard_id)
        return None


    def update_starting_blocks(self):
        base_chain_tip = self.forkchoice_on_shard('')

        # get the most recent merge block on shard '0'
        merge_block = self.previous_merge_block_on_shard(base_chain_tip, '', '0')
        if merge_block:
            self.starting_blocks['0'] = merge_block

        # get the most recent merge block on shard '0'
        merge_block = self.previous_merge_block_on_shard(base_chain_tip, '', '1')
        if merge_block:
            self.starting_blocks['1'] = merge_block

    def forkchoice_on_shard(self, shard_id):
        return forkchoice.get_shard_fork_choice(
            self.starting_blocks[shard_id],
            self.children,
            self.latest_messages_on_shard[shard_id],
            shard_id
        )


    def update_safe_estimates(self, validator_set):
        """Checks safety on messages in views forkchoice, and updates last_finalized_block"""
        pass

        # check the safety of the top shard!
        tip = self.forkchoice_on_shard('')

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

        # set starting messages! (should only happen initially)
        if None in message.estimate['prev_blocks']:
            assert not message.is_merge_block
            shard_id = r.sample(message.estimate['shard_ids'], 1)[0]
            print("Adding starting block for {}".format(shard_id))
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

            assert message.sender in self.latest_messages_on_shard[shard_id]

        # update children dictonary
        for parent in message.estimate['prev_blocks']:
            if parent not in self.children:
                self.children[parent] = set()
            self.children[parent].add(message)

        # preferably, would update starting blocks here.
