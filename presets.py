from settings import NUM_VALIDATORS, VALIDATOR_NAMES, WEIGHTS, REPORT_INTERVAL, NUM_MESSAGES_PER_ROUND, REPORT_SUBJECTIVE_VIEWS
import random as r

#default function args defined once, which is both efficient and, if mutable, can store state

def random(pairs=[[i, j] for i in xrange(NUM_VALIDATORS) for j in xrange(NUM_VALIDATORS) if not i == j]):
    return r.sample(pairs, NUM_MESSAGES_PER_ROUND)

def round_robin(msg=[0, 1]):
    to_return = [[msg[0], msg[1]]]
    msg[0] = (msg[0] + 1) % NUM_VALIDATORS
    msg[1] = (msg[1] + 1) % NUM_VALIDATORS
    return to_return

def full_propagation(pairs=[[i, j] for i in xrange(NUM_VALIDATORS) for j in xrange(NUM_VALIDATORS) if not i == j]):
    return pairs
