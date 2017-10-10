import unittest
import settings as s
import random as r
import utils


class TestUtils(unittest.TestCase):

    def test_get_weight_increasing(self):
        weights = [i for i in xrange(10)]
        s.update(weights)
        self.assertEqual(utils.get_weight(s.VALIDATOR_NAMES), 45)

    def test_get_weight_decreasing(self):
        weights = [i for i in xrange(9, -1, -1)]
        s.update(weights)

        self.assertEqual(utils.get_weight(s.VALIDATOR_NAMES), 45)

    def test_get_weight_random(self):
        weights = [r.random() for i in xrange(10)]
        s.update(weights)

        self.assertEqual(utils.get_weight(s.VALIDATOR_NAMES), sum(weights))

    def test_get_weight_partial_set(self):
        weights = [i*2 for i in xrange(10)]
        s.update(weights)

        subset = set([0, 1, 2, 3])
        self.assertEqual(utils.get_weight(subset), 12)

    def test_get_weight_partial_list(self):
        weights = [i*2 for i in xrange(10)]
        s.update(weights)

        self.assertEqual(utils.get_weight([0, 1, 2, 3]), 12)

    def test_get_weight_none(self):
        weight = utils.get_weight(None)
        self.assertEqual(weight, 0)

    def test_get_weight_empty(self):
        weight = utils.get_weight(set())
        self.assertEqual(weight, 0)


if __name__ == "__main__":
    unittest.main()
