"""The model bet module ... """
import casper.settings as s


class ModelBet:
    """For now, this simplies the bet structure to work with the adversary
    with no side-effects - so, no justifications necessary!"""

    def __init__(self, estimate, sender):

        # be safe. type check!...
        assert sender in s.VALIDATOR_NAMES, "...expected a validator!"

        # these are the key elements of a bet
        self.sender = sender
        self.estimate = estimate

    def __eq__(self, bet):
        if not bet:
            return False

        assert isinstance(B, ModelBet), "...model_bets can only equal model_bets!"

        return self.sender == bet.sender and self.estimate == bet.estimate


    @profile
    def __hash__(self):
        return hash(str(self.sender) + str(self.estimate))
