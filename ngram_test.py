import unittest
from ngram import Ngram

class NgramTests(unittest.TestCase):

  def mock_ngram(self, string, count, frequency, sig_score):
    ngram = Ngram(string)
    ngram.count = count
    ngram.frequency = frequency
    ngram.sig_score = sig_score
    return ngram

  def setUp(self):
    ngram_after_1 = self.mock_ngram('bar', 1, 1, 1)
    ngram_after_2 = self.mock_ngram('baz', 2, 2, 2)

    self.ngram = Ngram('foo', 1, 1)

    self.ngram.after[0][ngram_after_1.string] = ngram_after_1
    self.ngram.after[0][ngram_after_2.string] = ngram_after_2

    self.ngram.before[0][ngram_after_1.string] = ngram_after_1
    self.ngram.before[0][ngram_after_2.string] = ngram_after_2

  def test_get_after_count(self):
    self.assertEqual(
      self.ngram.get_after(sort_attribute="count"),
      [('baz', 2), ('bar', 1)]
    )

  def test_get_after_frequency(self):
    self.assertEqual(
      self.ngram.get_after(sort_attribute="frequency"),
      [('baz', 2), ('bar', 1)]
    )

  def test_get_after_sig_score(self):
    self.assertEqual(
      self.ngram.get_after(sort_attribute="sig_score"),
      [('baz', 2), ('bar', 1)]
    )

  def test_get_before_count(self):
    self.assertEqual(
      self.ngram.get_before(sort_attribute="count"),
      [('baz', 2), ('bar', 1)]
    )

  def test_get_before_frequency(self):
    self.assertEqual(
      self.ngram.get_before(sort_attribute="frequency"),
      [('baz', 2), ('bar', 1)]
    )

  def test_get_before_sig_score(self):
    self.assertEqual(
      self.ngram.get_before(sort_attribute="sig_score"),
      [('baz', 2), ('bar', 1)]
    )

if __name__ == '__main__':
  unittest.main()
