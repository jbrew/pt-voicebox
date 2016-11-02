from __future__ import absolute_import

import unittest

from voicebox.ngram import Ngram


class NgramTests(unittest.TestCase):

    @staticmethod
    def mock_ngram(string, count, frequency, sig_score):
        ngram = Ngram(string)
        ngram.count = count
        ngram.frequency = frequency
        ngram.sig_score = sig_score
        return ngram

    def setUp(self):
        ngram_after_1 = self.mock_ngram('bar', 1, 2, 3)
        ngram_after_2 = self.mock_ngram('baz', 7, 8, 9)

        self.ngram = Ngram('foo', 1, 1)

        self.ngram.after[0][ngram_after_1.string] = ngram_after_1
        self.ngram.after[0][ngram_after_2.string] = ngram_after_2

        self.ngram.before[0][ngram_after_1.string] = ngram_after_1
        self.ngram.before[0][ngram_after_2.string] = ngram_after_2

    def test_get_after__sort_attribute_count(self):
        self.assertEqual(
            self.ngram.get_after(sort_attribute="count"),
            [('baz', 7), ('bar', 1)]
        )

    def test_get_after__sort_attribute_frequency(self):
        self.assertEqual(
            self.ngram.get_after(sort_attribute="frequency"),
            [('baz', 8), ('bar', 2)]
        )

    def test_get_after__sort_attribute_sig_score(self):
        self.assertEqual(
            self.ngram.get_after(sort_attribute="sig_score"),
            [('baz', 9), ('bar', 3)]
        )

    def test_get_before__sort_attribute_count(self):
        self.assertEqual(
            self.ngram.get_before(sort_attribute="count"),
            [('baz', 7), ('bar', 1)]
        )

    def test_get_before__sort_attribute_frequency(self):
        self.assertEqual(
            self.ngram.get_before(sort_attribute="frequency"),
            [('baz', 8), ('bar', 2)]
        )

    def test_get_before__sort_attribute_sig_score(self):
        self.assertEqual(
            self.ngram.get_before(sort_attribute="sig_score"),
            [('baz', 9), ('bar', 3)]
        )


if __name__ == '__main__':
    unittest.main()
