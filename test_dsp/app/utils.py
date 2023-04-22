import random


def should_happen(percents):
    return random.random() < (float(percents) / 100.0)
