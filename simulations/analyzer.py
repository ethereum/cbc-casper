class Analyzer:
    def __init__(self, simulation):
        self.simulation = simulation

    def num_messages(self):
        return len(self.simulation.blockchain)

    def num_safe_messages(self):
        return len(self.simulation.safe_blocks)

    def orphan_rate(self):
        # does not take into account that some messages exist
        # with sequence number greater than last finalized message
        return float(self.num_messages() - self.num_safe_messages()) / self.num_messages()
