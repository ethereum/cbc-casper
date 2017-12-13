import sys
from simulations.validator_client import ValidatorClient


class SimulationRunner:
    def __init__(
            self,
            validator_set,
            msg_strategy,
            protocol,
            network,
            total_rounds,
            report_interval,
            display,
            save,
    ):
        self.validator_set = validator_set
        self.validator_clients = [
            ValidatorClient(validator, network) for validator in validator_set
        ]
        for validator_client in self.validator_clients:
            validator_client.should_make_new_message = msg_strategy

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

        self.network = network

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
        self._advance_time()

        received_messages = self._receive_messages()
        self._update_safe_estimates(received_messages.keys())

        self._generate_new_messages()

        self.plot_tool.update()
        if self.round % self.report_interval == self.report_interval - 1:
            self.plot_tool.plot()

    def _advance_time(self):
        self.round += 1
        self.network.set_time(self.round)
        for validator_client in self.validator_clients:
            validator_client.set_time(self.round)

    def _receive_messages(self):
        received_messages = {}
        for validator_client in self.validator_clients:
            messages = validator_client.retrieve_messages()
            if messages:
                received_messages[validator_client.validator] = messages
        return received_messages

    def _generate_new_messages(self):
        new_messages = []
        for validator_client in self.validator_clients:
            message = validator_client.make_and_propagate_message()
            if message:
                new_messages.append(message)
        return new_messages

    def _update_safe_estimates(self, validators):
        for validator in validators:
            validator.update_safe_estimates()
        self.network.global_view.update_safe_estimates(self.validator_set)

    def _send_initial_messages(self):
        """ ensures that initial messages are attempted to be propogated.
            requirement for any protocol where initial message is not shared """
        for validator in self.validator_set:
            self.network.send_to_all(validator.initial_message)
