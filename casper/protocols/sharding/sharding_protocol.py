from casper.protocols.sharding.sharding_view import ShardingView
from casper.protocols.sharding.block import Block
from casper.protocols.sharding.sharding_plot_tool import ShardingPlotTool
from casper.protocol import Protocol


class ShardingProtocol(Protocol):
    View = ShardingView
    Message = Block
    PlotTool = ShardingPlotTool

    shard_genesis_blocks = dict()


    # Shard ID's look like this:
    #       ''
    #     /    \
    #   '0'    '1'
    #  /  \    /  \
    #'00''01''10''11'
    #

    # Blocks can be merge mined between shards if
    # there is an edge between shards
    # That is, for ids shard_1 and shard_2, there can be a merge block if
    # abs(len(shard_1) - len(shard_2)) = 1 AND
    # for i in range(min(len(shard_1), len(shard_2))):
    #    shard_1[i] = shard_2[i]

    genesis_block = None
    current_shard = 0
    num_validators_assigned = 0 # for now, assign at least 3 validators!

    @classmethod
    def initial_message(cls, validator):
        """Returns a dict from shard_id -> shard genesis block"""
        # hard coded for now (3 is a arbitrary :-) )

        if cls.num_validators_assigned == 0:
            if '' not in cls.shard_genesis_blocks:
                estimate = {'prev_blocks': set([None]), 'shard_ids': set([''])}
                cls.shard_genesis_blocks[''] = Block(estimate, dict(), validator, -1, 0)
            cls.num_validators_assigned = 1
            return cls.shard_genesis_blocks['']
        elif cls.num_validators_assigned == 1:
            if '0' not in cls.shard_genesis_blocks:
                estimate = {'prev_blocks': set([None]), 'shard_ids': set(['0'])}
                cls.shard_genesis_blocks['0'] = Block(estimate, dict(), validator, -1, 0)
            cls.num_validators_assigned = 2
            return cls.shard_genesis_blocks['0']
        else:
            if '1' not in cls.shard_genesis_blocks:
                estimate = {'prev_blocks': set([None]), 'shard_ids': set(['1'])}
                cls.shard_genesis_blocks['1'] = Block(estimate, dict(), validator, -1, 0)
            cls.num_validators_assigned = 0
            return cls.shard_genesis_blocks['1']
