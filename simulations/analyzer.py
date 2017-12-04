import statistics

import casper.utils as utils


class Analyzer:
    def __init__(self, simulation):
        self.simulation = simulation
        self.global_view = simulation.network.global_view

    @property
    def num_messages(self):
        return len(self.messages())

    @property
    def num_safe_messages(self):
        return len(self.safe_messages())

    @property
    def num_unsafe_messages(self):
        return len(self.unsafe_messages())

    @property
    def num_bivalent_messages(self):
        return len(self.bivalent_messages())

    @property
    def prop_safe_messages(self):
        return float(self.num_safe_messages) / self.num_messages

    @property
    def safe_to_tip_length(self):
        return self.global_view.estimate().height - self.safe_tip_height

    @property
    def safe_tip_height(self):
        if self.safe_tip:
            return self.safe_tip.height
        return 0

    @property
    def bivalent_message_depth(self):
        max_height = max(
            message.height
            for message in self.global_view.latest_messages.values()
        )
        return max_height - self.safe_tip_height

    @property
    def bivalent_message_branching_factor(self):
        to_check = set(self.bivalent_messages())
        if self.safe_tip:
            to_check.add(self.safe_tip)

        check = to_check.pop()
        branches = 0
        num_checked = 0
        while check:
            if check in self.global_view.children:
                branches += len(self.global_view.children[check])
                num_checked += 1
            if not to_check:
                break
            check = to_check.pop()

        if num_checked == 0:
            return 0
        return branches / num_checked

    @property
    def safe_tip(self):
        return self.global_view.last_finalized_block

    @property
    def latency_to_finality(self):
        safe_messages = self.safe_messages()

        if not any(safe_messages):
            return None

        individual_latency = [
            self.global_view.when_finalized[message] - self.global_view.when_added[message]
            for message in safe_messages
        ]

        return statistics.mean(individual_latency)

    @property
    def orphan_rate(self):
        num_unsafe_messages = self.num_unsafe_messages
        num_safe_messages = self.num_safe_messages
        if num_unsafe_messages + num_safe_messages == 0:
            return 0
        return float(num_unsafe_messages) / (num_unsafe_messages + num_safe_messages)

    def messages(self):
        return set(self.global_view.justified_messages.values())

    def safe_messages(self):
        if not self.global_view.last_finalized_block:
            return set()

        return set(
            map(
                lambda link: link[0],
                utils.build_chain(self.global_view.last_finalized_block, None)
            )
        )

    def bivalent_messages(self):
        return self.messages() - self.safe_messages() - self.unsafe_messages()

    def unsafe_messages(self):
        potential = self.messages() - self.safe_messages()

        if not self.safe_tip:
            return set()

        return {
            message for message in potential
            if message.height <= self.safe_tip.height
        }
