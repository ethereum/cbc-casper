from casper.protocols.sharding.sharding_view import ShardingView
from casper.protocols.sharding.block import Block
from casper.protocols.sharding.sharding_plot_tool import ShardingPlotTool
from casper.protocol import Protocol


class ShardingProtocol(Protocol):
    View = ShardingView
    Message = Block
    PlotTool = ShardingPlotTool

    shard_genesis_blocks = dict()
    curr_shard_idx = 0
    curr_shard_ids = ['']

    """Shard ID's look like this:
           ''
         /    \
       '0'    '1'
      /  \    /  \
    '00''01''10''11'


     Blocks can be merge mined between shards if
     there is an edge between shards
     That is, for ids shard_1 and shard_2, there can be a merge block if
     abs(len(shard_1) - len(shard_2)) = 1 AND
     for i in range(min(len(shard_1), len(shard_2))):
        shard_1[i] = shard_2[i]
    """

    @classmethod
    def initial_message(cls, validator):
        """Returns a dict from shard_id -> shard genesis block"""
        shard_id = cls.get_new_shard_id()

        estimate = {'prev_blocks': set([None]), 'shard_ids': set([shard_id])}
        cls.shard_genesis_blocks[''] = Block(estimate, dict(), validator, -1, 0)

        return cls.shard_genesis_blocks['']

    @classmethod
    def get_new_shard_id(cls):
        new_id = cls.curr_shard_ids[cls.curr_shard_idx]
        cls.curr_shard_idx += 1

        if cls.curr_shard_idx == len(cls.curr_shard_ids):
            new_ids = []
            for shard_id in cls.curr_shard_ids:
                new_ids.append(shard_id + '0')
                new_ids.append(shard_id + '1')

            cls.curr_shard_idx = 0
            cls.curr_shard_ids = new_ids

        return new_id
