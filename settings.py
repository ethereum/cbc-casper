import random as r  # to ensure the tie-breaking property

r.seed()

# the size of the validator set is assumed to be known in advance
NUM_VALIDATORS = 5

# we will refer to them by names in this set
VALIDATOR_NAMES = set(range(NUM_VALIDATORS))

# we will give the validators random weights in 0.,BIGINT...
# ...this "big" integer's job is to guarantee the "tie-breaking property", of these random weights...
# ...that no two subsets of validator's total weights are exactly equal,
# ...in depoyment, we will add a random epsilon to the weights given by bond amounts.
# ...however, for the purposes of this work, we only only the "tie-breaking" property
BIGINT = 1000000000000

# behold, the binary estimate space!...
# it's a bit underwhelming, sure, but it's foundational
ESTIMATE_SPACE = set([0, 1])

# here they are... !
WEIGHTS = dict()
for v in VALIDATOR_NAMES:
    WEIGHTS[v] = max(20, r.gauss(mu=60, sigma=40)) + 1.0/(BIGINT + r.uniform(0, 1))

# behold, the binary estimate space!...
# it's a bit underwhelming, sure, but it's foundational
ESTIMATE_SPACE = set([0, 1])

# experiment variables:

NUM_MESSAGES_PER_ROUND = 1 #(NUM_VALIDATORS*NUM_VALIDATORS - NUM_VALIDATORS)
REPORT_INTERVAL = 2
REPORT_SUBJECTIVE_VIEWS = False
