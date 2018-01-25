"""The order view module extends a view for order data structures """
from casper.safety_oracles.clique_oracle import CliqueOracle
from casper.abstract_view import AbstractView
import casper.protocols.order.order_estimator as estimator


class OrderView(AbstractView):
    """A view class that also keeps track of a last_finalized_estimate"""
    def __init__(self, messages=None, first_message=None):
        super().__init__(messages)

        self.last_finalized_estimate = None
        self.last_fault_tolerance = 0

    def estimate(self):
        """Returns the current forkchoice in this view"""
        return estimator.get_estimate_from_latest_messages(
            self.latest_messages
        )

    def update_safe_estimates(self, validator_set):
        """Checks safety on most recent created by this view"""
        # check estimate safety on the most
        for bet in self.latest_messages.values():
            oracle = CliqueOracle(bet, self, validator_set)
            fault_tolerance, _ = oracle.check_estimate_safety()

            if fault_tolerance > 0:
                if self.last_finalized_estimate:
                    assert not self.last_finalized_estimate.conflicts_with(bet)
                self.last_fault_tolerance = fault_tolerance
                self.last_finalized_estimate = bet
                break
