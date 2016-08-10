import unittest
import test_data
from corpus import Corpus

class CorpusTests(unittest.TestCase):

  def _get_suggested_word_list(self, suggested_tuples):
    return set(map(lambda (word, sort_attribute): word, suggested_tuples))

  def _get_suggested_sort_attribute(self, suggested_tuples, word):
    index = [t[0] for t in suggested_tuples].index(word)
    return suggested_tuples[index][1]

  def test_suggest__text_small(self):
    corpus = Corpus(text=test_data.text_small)

    suggested_tuples = corpus.suggest([], 0, 2)
    self.assertEqual(
      self._get_suggested_word_list(suggested_tuples),
      set(['a', 'penny'])
    )
    self.assertEqual(
      self._get_suggested_sort_attribute(suggested_tuples, 'a'),
      self._get_suggested_sort_attribute(suggested_tuples,  'penny')
    )

    suggested_tuples = corpus.suggest(['a'], 1, 2)
    self.assertEqual(
      self._get_suggested_word_list(suggested_tuples),
      set(['a', 'penny'])
    )
    self.assertGreater(
      self._get_suggested_sort_attribute(suggested_tuples, 'penny'),
      self._get_suggested_sort_attribute(suggested_tuples,  'a')
    )

    suggested_tuples = corpus.suggest(['a', 'penny'], 2, 2)
    self.assertEqual(
      self._get_suggested_word_list(suggested_tuples),
      set(['saved', 'earned'])
    )
    self.assertEqual(
      self._get_suggested_sort_attribute(suggested_tuples, 'saved'),
      self._get_suggested_sort_attribute(suggested_tuples,  'earned')
    )

  def test_suggest__text_small_min_word_count(self):
    corpus = Corpus(text=test_data.text_small, min_word_count=2)

    suggested_tuples = corpus.suggest([], 0, 2)
    self.assertEqual(
      self._get_suggested_word_list(suggested_tuples),
      set(['a', 'penny'])
    )
    self.assertEqual(
      self._get_suggested_sort_attribute(suggested_tuples, 'a'),
      self._get_suggested_sort_attribute(suggested_tuples,  'penny')
    )

    suggested_tuples = corpus.suggest(['a'], 1, 2)
    self.assertEqual(
      self._get_suggested_word_list(suggested_tuples),
      set(['a', 'penny'])
    )
    self.assertGreater(
      self._get_suggested_sort_attribute(suggested_tuples, 'penny'),
      self._get_suggested_sort_attribute(suggested_tuples,  'a')
    )

    suggested_tuples = corpus.suggest(['a', 'penny'], 2, 2)
    self.assertEqual(
      self._get_suggested_word_list(suggested_tuples),
      set(['a', 'penny'])
    )
    self.assertEqual(
      self._get_suggested_sort_attribute(suggested_tuples, 'a'),
      self._get_suggested_sort_attribute(suggested_tuples,  'penny')
    )

if __name__ == '__main__':
  unittest.main()
