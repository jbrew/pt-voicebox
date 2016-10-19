from __future__ import absolute_import
import six
from six.moves import range
__author__ = 'jamiebrew'

from ngram import Ngram
import string
import math
import operator
import re

"""
a corpus represents information about a text as a tree indexed by string
	* each entry in the tree is an ngram object
	* the key for a multi-word ngram is the space-separated words in the ngram
"""
class Corpus(object):

    def __init__(self, text, name='', max_ngram_size=2, sort_attribute='frequency', foresight=0, hindsight=2, min_word_count=1):
        self.text = text
        self.name = name
        self.max_ngram_size = max_ngram_size
        self.sort_attribute = sort_attribute
        self.foresight = foresight
        self.hindsight = hindsight
        self.min_word_count = min_word_count

        self.wordcount = 0
        self.tree = {}
        self.make_tree()

    # The list of words in a given list of sentences that have a count greater than
    # or equal to the minimum word count
    def get_white_list(self, sentences):
        word_count = {}
        for sentence in sentences:
            for word in sentence:
                word_count[word] = word_count.get(word, 0) + 1

        white_list = set()
        for word, count in six.iteritems(word_count):
            if count >= self.min_word_count:
                white_list.add(word)

        return white_list

    # constructs the tree of ngrams' likelihood of following other ngrams
    def make_tree(self):
        sentences = self.get_sentences()
        white_list = self.get_white_list(sentences)

        # go through each sentence, add each word to the dictionary, incrementing length each time
        for sentence in sentences:
            sentence = ['START_SENTENCE'] + sentence
            for ngram_size in range(0, self.max_ngram_size+1):
                for start in range(0, len(sentence)):
                    end = start + ngram_size
                    if end <= len(sentence):
                        words_to_add = sentence[start:end]
                        if set(words_to_add) < white_list and len(words_to_add) > 0: # checks that all of the words in the ngram pass criterion
                            new_ngram = " ".join(words_to_add)
                            self.add_ngram(new_ngram)
                            if ngram_size == 1:
                                self.wordcount += 1

                            # add dictionaries of words following this ngram
                            for word_position in range(end, end+self.hindsight):
                                if word_position < len(sentence):
                                    reach = word_position - end
                                    target = self.tree[new_ngram].after[reach]
                                    word = sentence[word_position]
                                    if word in white_list:
                                        self.add_ngram(word, target)

                            # add dictionaries of words preceding this ngram
                            for word_position in range(start-1, start-self.foresight-1, -1):
                                if word_position >= 0:
                                    reach = start - word_position
                                    target = self.tree[new_ngram].before[reach-1]
                                    word = sentence[word_position]
                                    if word in white_list:
                                        self.add_ngram(word, target)

        self.calculate_frequencies()
        self.calculate_sig_scores()

    # Split text into sentences, lowercase and clean punctuation
    def get_sentences(self):
        sentences = self.text.split('.\n' or '. ' or '?' or '!')

        return [(
                sentence.strip('\n') \
                        .translate(string.maketrans('', ''), string.punctuation.replace('\'', '')) \
                        .lower()
                        .split()
            ) for sentence in sentences]

    # Adds an ngram to a given tree
    def add_ngram(self, ngram, tree=None):
        tree = self.tree if tree is None else tree

        if ngram in tree:
            tree[ngram].count += 1
        else:
            tree[ngram] = Ngram(ngram, self.hindsight, self.foresight)

    # Finds and stores normalized frequencies
    def calculate_frequencies(self):
        for _, ngram in six.iteritems(self.tree):
            ngram.frequency = ngram.count / float(self.wordcount)
            for ngrams_before in ngram.before:
                for _, ngram_before in six.iteritems(ngrams_before):
                    ngram_before.frequency = ngram_before.count / float(ngram.count)
            for ngrams_after in ngram.after:
                for _, ngram_after in six.iteritems(ngrams_after):
                    ngram_after.frequency = ngram_after.count / float(ngram.count)

    # Computes and stores the significance scores
    def calculate_sig_scores(self):
        for _, ngram in six.iteritems(self.tree):
            for ngrams_before in ngram.before:
                for before_key, ngram_before in six.iteritems(ngrams_before):
                    ngram_before.sig_score = (ngram_before.frequency / self.tree[before_key].frequency) * math.log(ngram.frequency + 1, 10)
            for ngrams_after in ngram.after:
                for after_key, ngram_after in six.iteritems(ngrams_after):
                    ngram_after.sig_score = (ngram_after.frequency / self.tree[after_key].frequency) * math.log(ngram.frequency + 1, 10)

    # given a sentence and an insertion position in that sentence, yields a list of words likely to occur at that position
    # based on adjacent words and baseline frequency
    def suggest(self, sentence, cursor_position, num_words):

        # these are the parts of the active sentence that come before and after the cursor
        before_cursor = sentence[0:cursor_position]
        after_cursor = sentence[cursor_position:]

        suggestions = {}

        # look at previous words in sentence, and all the words occurring after them
        for reach in range(1, self.hindsight+1):
            for ngram_size in range(1, self.max_ngram_size+1):
                if len(before_cursor)+1 >= reach+ngram_size:
                    end_of_ngram = len(before_cursor)-reach
                    start_of_ngram = end_of_ngram - (ngram_size-1)
                    previous_ngram = " ".join(before_cursor[start_of_ngram:end_of_ngram+1])
                    after_previous = self.get_after(previous_ngram, reach, num_words)
                    #print "after %s: %s" % (previous_ngram, str(after_previous))
                    # crude function for privileging larger n-grams and closer contexts
                    weight = (10**ngram_size)/(10**reach)
                    for tuple in after_previous:
                        key = tuple[0]
                        value = tuple[1] * weight
                        if len(key.split(' ')) == 1:
                            if key not in suggestions:
                                suggestions[key] = value
                            else:
                                suggestions[key] += value

        for reach in range(1, self.foresight+1):
            for ngram_size in range(1, self.max_ngram_size+1):
                if len(after_cursor)+1 >= reach+ngram_size:
                    start_of_ngram = reach - 1
                    end_of_ngram = start_of_ngram + (ngram_size - 1)
                    next_ngram = " ".join(after_cursor[start_of_ngram:end_of_ngram+1])
                    before_next = self.get_before(next_ngram, reach, num_words)
                    #print "before %s: %s" % (next_ngram.string, str(before_next))

                    # crude function for privileging larger n-grams and closer contexts
                    weight = (10**ngram_size)/(10**reach)
                    for tuple in before_next:
                        key = tuple[0]
                        value = tuple[1] * weight
                        if len(key.split(' ')) == 1:
                            if key not in suggestions:
                                suggestions[key] = value
                            else:
                                suggestions[key] += value

        baseline_weight = 0.00000001
        for key in self.tree:
            ngram = self.tree[key]
            value = baseline_weight * getattr(ngram, self.sort_attribute)
            if len(key.split(' ')) == 1:
                if key not in suggestions:
                    suggestions[key] = value
                else:
                    suggestions[key] += value

        suggestion_list = list(reversed(sorted(list(suggestions.items()), key=operator.itemgetter(1))))[0:num_words]

        return suggestion_list

    def get_before(self, key, distance=1, num_words = 20):
        if key in self.tree:
            return self.tree[key].get_before(distance, num_words, self.sort_attribute)
        else:
            return []

    def get_after(self, key, distance=1, num_words = 20):
        if key in self.tree:
            return self.tree[key].get_after(distance, num_words, self.sort_attribute)
        else:
            return []

    def list_of_words(self):
        return list(self.tree.keys())

    def __contains__(self, item):
        return item in self.tree

    def __getitem__(self, item):
        return self.tree[item]

    def __len__(self):
        return len(self.tree)


