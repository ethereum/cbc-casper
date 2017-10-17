"""The settings module ... """

# Used to ensure the tie-breaking property.
import random as r


def init():
    """Initialize all the default settings."""
    r.seed()

    # Declare our global variables.
    global ESTIMATE_SPACE
    global NUM_MESSAGES_PER_ROUND
    global REPORT_INTERVAL
    global REPORT_SUBJECTIVE_VIEWS

    # Behold, the binary estimate space!
    # It's a bit underwhelming, sure, but it's foundational.
    ESTIMATE_SPACE = set([0, 1])

    # Experiment variables:
    NUM_MESSAGES_PER_ROUND = 1
    REPORT_INTERVAL = 20
    REPORT_SUBJECTIVE_VIEWS = False


init()
