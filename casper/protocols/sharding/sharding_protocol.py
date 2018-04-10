import json
import random as r

from casper.utils import get_random_str
from casper.protocol import Protocol
from casper.protocols.sharding.sharding_view import ShardingView
from casper.protocols.sharding.block import Block
from casper.protocols.sharding.sharding_plot_tool import ShardingPlotTool


class ShardingProtocol(Protocol):
    """A protocol for coming to consensus on a sharded blockchain with merge blocks"""
    Message = Block
    View = ShardingView
    PlotTool = ShardingPlotTool

    def __init__(self, json_string, display, save, report_interval):
        parsed_json = self.parse_json(json_string)

        super().__init__(
            parsed_json['config']['validators'],
            parsed_json['execution']['execution_string'],
            parsed_json['execution']['msg_per_round'] * report_interval,
            display,
            save,
            ShardingPlotTool,
            ShardingView,
            Block
        )

        self.set_initial_messages(parsed_json['config']['num_shards'])

    @classmethod
    def parse_json(cls, json_string):
        parsed_json = json.loads(json_string)

        assert parsed_json['protocol'] == 'sharding'

        config = parsed_json['config']
        assert len(config['validators']) >= config['num_shards']

        return parsed_json

    def set_initial_messages(self, num_shards):
        shards = 0
        genesis_blocks = set()
        shard_id_gen = self.get_shard_id_gen()

        for validator in self.global_validator_set:
            if shards == num_shards:
                break

            shard_id = shard_id_gen()
            estimate = {'prev_blocks': set([None]), 'shard_ids': set([shard_id])}
            genesis = Block(estimate, dict(), validator, -1, 0)
            genesis_blocks.add(genesis)
            shards += 1

            self.register_message(genesis, get_random_str(10))

        for validator in self.global_validator_set:
            validator.initialize_view(genesis_blocks)


    def get_shard_id_gen(self):
        curr_list = ['']
        curr_idx = 0

        def gen():
            nonlocal curr_list, curr_idx
            next_id = curr_list[curr_idx]
            curr_idx += 1

            if curr_idx == len(curr_list):
                next_list = []
                for id in curr_list:
                    next_list.append(id + '0')
                    next_list.append(id + '1')

                curr_list = next_list
                curr_idx = 0

            return next_id
        return gen
