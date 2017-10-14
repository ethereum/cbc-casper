"""The settings module ... """

# Used to ensure the tie-breaking property.
import random as r


def init():
    """Initialize all the default settings."""
    r.seed()

    # Declare our global variables.
    global NUM_VALIDATORS
    global VALIDATOR_NAMES
    global ESTIMATE_SPACE
    global WEIGHTS
    global TOTAL_WEIGHT
    global NUM_MESSAGES_PER_ROUND
    global REPORT_INTERVAL
    global REPORT_SUBJECTIVE_VIEWS

    # The size of the validator set is assumed to be known in advance.
    NUM_VALIDATORS = 5

    # We will refer to them by names in this set.
    VALIDATOR_NAMES = set(range(NUM_VALIDATORS))

    # We will give the validators random weights in 0.,BIGINT;
    # this "big" integer's job is to guarantee the "tie-breaking property", of these random
    # weights that no two subsets of validator's total weights are exactly equal.
    # In deployment, we will add a random epsilon to the weights given by bond amounts.
    # However, for the purposes of this work, we only only the "tie-breaking" property.
    BIGINT = 1000000000000

    # Behold, the binary estimate space!
    # It's a bit underwhelming, sure, but it's foundational.
    ESTIMATE_SPACE = set([0, 1])

    # Here are the weights!
    WEIGHTS = {i: max(20, r.gauss(mu=60, sigma=40)) + 1.0/(BIGINT + r.uniform(0, 1)) + r.random() for i in VALIDATOR_NAMES}

    TOTAL_WEIGHT = sum(WEIGHTS.values())

    # Experiment variables:

    NUM_MESSAGES_PER_ROUND = 1 #(NUM_VALIDATORS*NUM_VALIDATORS - NUM_VALIDATORS)
    REPORT_INTERVAL = 20
    REPORT_SUBJECTIVE_VIEWS = False


def update(val_weights):
    """Update the global settings given new validator weights."""
    global NUM_VALIDATORS
    global VALIDATOR_NAMES
    global WEIGHTS
    global TOTAL_WEIGHT

    NUM_VALIDATORS = len(val_weights)
    VALIDATOR_NAMES = set(range(NUM_VALIDATORS))
    WEIGHTS = {i: val_weights[i] for i in VALIDATOR_NAMES}
    TOTAL_WEIGHT = sum(val_weights)


init()
