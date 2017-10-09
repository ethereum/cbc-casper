from testing_language import TestLangCBC
from block import Block
from justification import Justification
import unittest
import settings as s
import random as r
import copy

class TestUtils(unittest.TestCase):

    def test_equality_of_copies_off_genesis(self):
        s.update([10]) # necessary for now due to assertions during block creation
        block = Block(None, Justification(), 0)

        shallow_copy =  copy.copy(block)
        deep_copy = copy.deepcopy(block)

        self.assertEqual(block, shallow_copy)
        self.assertEqual(block, deep_copy)
        self.assertEqual(shallow_copy, deep_copy)


    def test_equality_of_copies_of_non_genesis(self):
        test_string = "B0-A S1-A B1-B S0-B B0-C S1-C B1-D S0-D H0-D"
        testLang = TestLangCBC(test_string, [10, 11])
        testLang.parse()

        for b in testLang.blocks:
            shallow_copy =  copy.copy(b)
            deep_copy = copy.deepcopy(b)

            self.assertEqual(b, shallow_copy)
            self.assertEqual(b, deep_copy)
            self.assertEqual(shallow_copy, deep_copy)

    def test_non_equality_of_copies_off_genesis(self):
        s.update([10, 11])
        block_0 = Block(None, Justification(), 0)
        block_1 = Block(None, Justification(), 1)

        self.assertNotEqual(block_0, block_1)

    def test_non_equality_of_copies_of_non_genesis(self):
        test_string = "B0-A S1-A B1-B S0-B B0-C S1-C B1-D S0-D H0-D"
        testLang = TestLangCBC(test_string, [10, 11])
        testLang.parse()

        num_equal = 0
        for b in testLang.blocks:
            for b1 in testLang.blocks:
                if b1 == b:
                    num_equal += 1
                    continue

                self.assertNotEqual(b, b1)

        self.assertEqual(num_equal, len(testLang.blocks))


    def test_not_in_blockchain_off_genesis(self):
        s.update([10, 11])
        block_0 = Block(None, Justification(), 0)
        block_1 = Block(None, Justification(), 1)

        self.assertFalse(block_0.is_in_blockchain(block_1))

    def test_in_blockchain(self):
        test_string = "B0-A S1-A B1-B S0-B B0-C S1-C B1-D S0-D H0-D"
        testLang = TestLangCBC(test_string, [11, 10])
        testLang.parse()

        prev = testLang.blocks['A']
        for b in ['B', 'C', 'D']:
            block = testLang.blocks[b]
            self.assertTrue(prev.is_in_blockchain(block))
            self.assertFalse(block.is_in_blockchain(prev))

            prev = block


if __name__ == "__main__":
    unittest.main()
