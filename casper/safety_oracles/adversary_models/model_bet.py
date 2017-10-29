"""The model bet module ... """


class ModelBet(object):
    """Simple bet structure for binary consensus for side effect free adversary"""

    def __init__(self, estimate, sender):
        # these are the key elements of a bet
        self.sender = sender
        self.estimate = estimate

    def __eq__(self, bet):
        if not bet:
            return False

        assert isinstance(bet, ModelBet), "...model_bets can only equal model_bets!"

        return self.sender == bet.sender and self.estimate == bet.estimate

    def __hash__(self):
        return hash(str(self.sender) + str(self.estimate))
