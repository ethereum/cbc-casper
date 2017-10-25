class Analyzer:
    def __init__(self, simulation):
        self.simulation = simulation
        self.global_view = simulation.network.global_view

    def num_messages(self):
        return len(self.messages())

    def num_safe_messages(self):
        return len(self.safe_messages())

    def num_unsafe_messages(self):
        return len(self.unsafe_messages())

    def messages(self):
        return self.global_view.messages

    def safe_messages(self):
        return set(self.simulation.safe_blocks)

    def safe_tip(self):
        if not self.simulation.safe_blocks:
            return None

        return self.simulation.safe_blocks[-1]

    def unsafe_messages(self):
        potential = self.messages() - self.safe_messages()

        if not self.safe_tip():
            return set()

        return {
            message for message in potential
            if not self.safe_tip().is_in_blockchain(message)
        }

    def orphan_rate(self):
        # does not take into account that some messages exist
        # with sequence number greater than last finalized message
        num_unsafe_messages = self.num_unsafe_messages()
        num_safe_messages = self.num_safe_messages()
        if num_unsafe_messages + num_safe_messages == 0:
            return 0
        return float(num_unsafe_messages) / (num_unsafe_messages + num_safe_messages)
