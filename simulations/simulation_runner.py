import sys

from casper.networks import StepNetwork
from casper.protocols.blockchain.blockchain_protocol import BlockchainProtocol


class SimulationRunner:
    def __init__(
            self,
            validator_set,
            msg_gen,
            protocol,
            total_rounds,
            report_interval,
            display,
            save,
            force_justify_messages=False
    ):
        self.validator_set = validator_set
        self.msg_gen = msg_gen
        self.save = save

        self.round = 0
        if total_rounds:
            self.total_rounds = total_rounds
        else:
            self.total_rounds = sys.maxsize

        if report_interval:
            self.report_interval = report_interval
        else:
            self.report_interval = 1

        self.network = StepNetwork(validator_set, protocol, force_justify_messages)

        self.plot_tool = protocol.PlotTool(display, save, self.network.global_view, validator_set)
        self.plot_tool.plot()

    def run(self):
        """ run simulation total_rounds if specified
            otherwise, run indefinitely """
        self._send_initial_messages()

        while self.round < self.total_rounds:
            self.step()

        if self.save:
            print("making gif")
            self.plot_tool.make_gif()

    def step(self):
        """ run one round of the simulation """
        """ this becomes, who is going to make a message and send to the network """
        """ rather than what explicit paths happen """
        self.round += 1
        new_messages = self._generate_new_messages()
        received_messages = self._receive_messages()
        self._update_safe_estimates(received_messages.keys())

        self.plot_tool.update(new_messages, received_messages)
        if self.round % self.report_interval == self.report_interval - 1:
            self.plot_tool.plot()

        self.network.time += 1

    def _generate_new_messages(self):
        validators = self.msg_gen(self.validator_set)
        new_messages = []
        for validator in validators:
            message = validator.make_new_message()
            self.network.send_to_all(message)
            new_messages.append(message)
        return new_messages

    def _receive_messages(self):
        received_messages = {}
        for validator in self.validator_set:
            messages = self.network.receive_all(validator)
            if messages:
                validator.receive_messages(set(messages))
                received_messages[validator] = messages
        return received_messages

    def _update_safe_estimates(self, validators):
        for validator in validators:
            validator.update_safe_estimates()
        self.network.global_view.update_safe_estimates(self.validator_set)

    def _send_initial_messages(self):
        """ ensures that initial messages are attempted to be propogated.
            requirement for any protocol where initial message is not shared """
        for validator in self.validator_set:
            self.network.send_to_all(validator.initial_message)

