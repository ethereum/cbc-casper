from time import sleep

from simulations.validator_client import ValidatorClient


class ThreadedSimulation:
    def __init__(
            self,
            validator_set,
            msg_strategy,
            protocol,
            network,
            total_rounds,
            report_interval,
            display=False,
            save=True
    ):
        self.length_in_seconds = total_rounds
        self.report_seconds = report_interval
        self.network = network
        self.validator_set = validator_set

        self.validator_clients = [
            ValidatorClient(validator, network) for validator in validator_set
        ]

        # currently monkey patches VC. Move to Strategy object in future
        for validator_client in self.validator_clients:
            validator_client.should_make_new_message = msg_strategy

        self.plot_tool = protocol.PlotTool(False, save, network.global_view, validator_set)

    def run(self):
        print("starting simulation")
        self._send_initial_messages()

        # run each validator_client in separate thread
        for validator_client in self.validator_clients:
            validator_client.start()

        for i in range(int(self.length_in_seconds / self.report_seconds)):
            print("plotting {}".format(i))
            self.plot_tool.update()
            self.plot_tool.plot()
            sleep(self.report_seconds)

        print("shutting down validators")
        for validator_client in self.validator_clients:
            validator_client.stop()

        print("making gif")
        self.plot_tool.make_gif()

    def _send_initial_messages(self):
        """ ensures that initial messages are attempted to be propogated.
            requirement for any protocol where initial message is not shared """
        for validator in self.validator_set:
            self.network.send_to_all(validator.initial_message)
