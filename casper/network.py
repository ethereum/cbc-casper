"""The network module .... """
import casper.settings as s

from casper.validator import Validator
from casper.view import View
import casper.plot_tool as plot_tool


class Network:
    """Simulates a network."""
    def __init__(self):
        self.validators = dict()
        for v in s.VALIDATOR_NAMES:
            self.validators[v] = Validator(v)
        self.global_view = View()

    def propagate_message_to_validator(self, message, validator_name):
        """Propogate a message to a validator."""
        assert message in self.global_view.messages, "expected only to propagate messages from the global view"
        self.validators[validator_name].receive_messages(set([message]))

    def get_message_from_validator(self, validator_name):
        """Get a message from a validator."""
        assert validator_name in s.VALIDATOR_NAMES, "expected a known validator"

        new_message = self.validators[validator_name].make_new_message()
        return new_message

    # def let_validator_push

    def view_initialization(self, view):
        assert isinstance(view, View)
        self.global_view = view.messages

        latest = view.latest_messages

        for v in latest:
            self.validators[v].receive_messages(set([latest[v]]))

    def random_initialization(self):
        for v in s.VALIDATOR_NAMES:
            new_bet = self.get_message_from_validator(v)
            self.global_view.add_messages(set([new_bet]))

    def report(self, colored_messages=set(), color_mag=dict(), edges=[]):
        plot_tool.plot_view(self.global_view, coloured_bets=colored_messages,
                            colour_mag=color_mag, edges=edges)
