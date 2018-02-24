"""The block module implements the message data structure for a sharded blockchain"""
from casper.message import Message
NUM_MERGE_SHARDS = 2


class Block(Message):
    """Message data structure for a sharded blockchain"""

    @classmethod
    def is_valid_estimate(cls, estimate):
        for key in ['prev_blocks', 'shard_ids']:
            if key not in estimate:
                return False
            if not isinstance(estimate[key], set):
                return False
        return True

    def on_shard(self, shard_id):
        return shard_id in self.estimate['shard_ids']

    def prev_block(self, shard_id):
        """Returns the previous block on the shard: shard_id
        Throws a KeyError if there is no previous block"""
        if shard_id not in self.estimate['shard_ids']:
            raise KeyError("No previous block on that shard")

        for block in self.estimate['prev_blocks']:
            # if this block is the genesis, previous is None
            if block is None:
                return None

            # otherwise, return the previous block on that shard
            if block.on_shard(shard_id):
                return block

        raise KeyError("Block on {}, but has no previous block on that shard!".format(shard_id))

    @property
    def is_merge_block(self):
        return len(self.estimate['shard_ids']) == NUM_MERGE_SHARDS

    @property
    def is_genesis_block(self):
        return None in self.estimate['prev_blocks']

    def conflicts_with(self, message):
        """Returns true if self is not in the prev blocks of other_message"""
        assert isinstance(message, Block), "...expected a block"

        return not self.is_in_blockchain(message, '')

    def is_in_blockchain(self, block, shard_id):
        """Could be a zero generation ancestor!"""
        if not block:
            return False

        if not block.on_shard(shard_id):
            return False

        if self == block:
            return True

        return self.is_in_blockchain(block.prev_block(shard_id), shard_id)
