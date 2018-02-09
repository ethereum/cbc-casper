"""The block module implements the message data structure for a sharded blockchain"""
from casper.message import Message


class Block(Message):
    """Message data structure for a sharded blockchain"""

    @classmethod
    def is_valid_estimate(cls, estimate):
        if not isinstance(estimate, dict):
            return False
        if not isinstance(estimate['prev_blocks'], set):
            return False
        if not isinstance(estimate['shard_ids'], set):
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
            if block is None:
                return None

            if block.on_shard(shard_id):
                return block

        raise KeyError("Should have found previous block on shard!")

    @property
    def is_merge_block(self):
        return len(self.estimate['shard_ids']) == 2

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
