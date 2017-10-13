import casper.settings as s

from casper.view import View
import casper.plot_tool as plot_tool


class Network:
    def __init__(self, validator_set):
        self.validator_set = validator_set
        self.global_view = View()

    def propagate_message_to_validator(self, message, validator):
        assert message in self.global_view.messages, "...expected only to propagate messages from the global view"
        assert validator in self.validator_set, "...expected a known validator"

        validator.receive_messages(set([message]))

    def get_message_from_validator(self, validator):
        assert validator in self.validator_set, "...expected a known validator"

        new_message = validator.make_new_message()
        self.global_view.add_messages(set([new_message]))

        return new_message

    def view_initialization(self, view):
        assert isinstance(view, View)
        self.global_view = view.messages

        latest = view.latest_messages

        for v in latest:
            self.validators[v].receive_messages(set([latest[v]]))

    def random_initialization(self):
        for v in self.validator_set:
            new_bet = self.get_message_from_validator(v)
            self.global_view.add_messages(set([new_bet]))

    def report(self, colored_messages=set(), color_mag=dict(), edges=[]):
        plot_tool.plot_view(self.global_view, coloured_bets=colored_messages, colour_mag=color_mag, edges=edges)
