__author__ = 'jamiebrew'

import ngram
import string
import math
import operator
import re
from collections import Counter

"""
a corpus represents information about a text as a tree indexed by string
	* each entry in the tree is an ngram object
	* the key for a multi-word ngram is the space-separated words in the ngram	
"""
class Corpus(object):

    def __init__(self, text, name, max_ngram_size = 2, sort_attribute = "FREQUENCY", foresight = 0, hindsight = 2, wordcount_criterion = 1):
        self.wordcount = 0
        self.wordcount_criterion = wordcount_criterion
        self.foresight = foresight
        self.hindsight = hindsight
        self.max_ngram_size = max_ngram_size
        self.tree = self.make_tree(text)
        self.name = name
        self.sort_attribute = sort_attribute

    # returns the n words occurring most frequently in a string
    def top_words(self, n, text):
        text = text.translate(string.maketrans("",""), string.punctuation)
        words = re.findall('[a-z]+', text.lower())
        wordcounts = Counter(words)
        sorted_wordcounts = list(reversed(sorted(wordcounts.items(), key=operator.itemgetter(1))))
        return sorted_wordcounts[0:n]

    # the list of words in a given list of sentences that meet a given wordcount criterion
    def short_list(self, sentence_list, wordcount_criterion):
        # all unique words mapped to wordcount
        unique_words = {}

        # make wordcount dictionary
        for sentence in sentence_list:
            for word in sentence:
                if word not in unique_words:
                    unique_words[word] = 1
                else:
                    unique_words[word] += 1
        shortlist = set()
        for word in unique_words:
            if unique_words[word] >= wordcount_criterion:
                shortlist.add(word)
        print "Unique words in corpus:", len(unique_words)
        print "Words occurring at least %s times: %s" % (wordcount_criterion, len(shortlist))
        return shortlist

    # constructs the tree of ngrams' likelihood of following other ngrams
    def make_tree(self, str):
        sentences = self.make_sentences(str)
        shortlist = self.short_list(sentences, self.wordcount_criterion)

        T = {}
        # go through each sentence, add each word to the dictionary, incrementing length each time
        for sentence in sentences:
            sentence = ['START_SENTENCE'] + sentence
            for ngram_size in range(0, self.max_ngram_size+1):
                for start in range(0, len(sentence)):
                    end = start + ngram_size
                    if end <= len(sentence):
                        words_to_add = sentence[start:end]
                        if set(words_to_add) < shortlist and len(words_to_add) > 0: # checks that all of the words in the ngram pass criterion
                            new_ngram = " ".join(words_to_add)
                            self.add_ngram(new_ngram, T)
                            if ngram_size==1:
                                self.wordcount += 1

                            # add dictionaries of words following this ngram
                            for word_position in range(end, end+self.hindsight):
                                if word_position < len(sentence):
                                    reach = word_position - end
                                    target = T[new_ngram].after[reach]
                                    word = sentence[word_position]
                                    if word in shortlist:
                                        self.add_ngram(word,target)

                            # add dictionaries of words preceding this ngram
                            for word_position in range(start-1, start-self.foresight-1, -1):
                                if word_position >= 0:
                                   reach = start - word_position
                                   target = T[new_ngram].before[reach-1]
                                   word = sentence[word_position]
                                   if word in shortlist:
                                        self.add_ngram(word,target)

        T = self.calculate_frequencies(T)
        T = self.calculate_sig_scores(T)
        return T

    # splits the text into sentences, lowercases them and cleans punctuation
    def make_sentences(self, str):
        # split at period followed by newline or space, or question mark, or exclamation point
        sentences = str.split('.\n' or '. ' or '?' or '!')

        for sentence in range (0,len(sentences)):
            sentences[sentence] = sentences[sentence].strip('\n')
            sentences[sentence] = sentences[sentence].translate(string.maketrans("",""), string.punctuation.replace("'","")) # removes all punctuation except apostrophe
            sentences[sentence] = sentences[sentence].lower()
            sentences[sentence] = sentences[sentence].split()
        return sentences

    # adds an ngram to a given tree
    def add_ngram(self, str, tree):
        if str in tree:
            tree[str].count += 1
        else:
            tree[str] = ngram.Ngram(str)
            tree[str].after = [{} for i in range(0,self.hindsight)]
            tree[str].before = [{} for i in range(0,self.foresight)]

    def lookup_ngram(self, ngram, tree):
        if ngram in tree:
            return tree[ngram]

    # given a tree that has kept count for each word, finds and stores normalized frequencies
    def calculate_frequencies(self,T):
        for ngram_key in T:
            ngram = T[ngram_key]
            ngram.frequency = ngram.count/float(self.wordcount)
            for dict in ngram.before:
                for before_key in dict:
                    before_ngram = dict[before_key]
                    before_ngram.frequency = before_ngram.count/float(ngram.count)
            for dict in ngram.after:
                for after_key in dict:
                    after_ngram = dict[after_key]
                    after_ngram.frequency = after_ngram.count/float(ngram.count)
        return T

    # given a tree that has frequencies for each word, computes and stores the significance scores
    def calculate_sig_scores(self,T):
        for n_gram_key in T:
            n_gram = T[n_gram_key]
            for dict in n_gram.before:
                for before_key in dict:
                    before_n_gram = dict[before_key]
                    before_n_gram.sig_score = (before_n_gram.frequency/T[before_key].frequency) * math.log(n_gram.frequency+1,10)
            for dict in n_gram.after:
                for after_key in dict:
                    after_n_gram = dict[after_key]
                    after_n_gram.sig_score = (after_n_gram.frequency/T[after_key].frequency) * math.log(n_gram.frequency+1,10)
        return T

    # ranks all ngrams in a tree by the specified attribute. returns a list
    def sort_ngrams(self, tree, sort_att):
        to_sort = {}
        for ngram_key in tree:
            ngram = tree[ngram_key]
            if sort_att == 'frequency':
                to_sort[ngram_key] = ngram.frequency
            elif sort_att == 'sigscore':
                to_sort[ngram_key] = ngram.sig_score
            elif sort_att == 'count':
                to_sort[ngram_key] = ngram.count
        return sorted(to_sort, key=operator.itemgetter(0))

    # given a sentence and an insertion position in that sentence, yields a list of words likely to occur at that position
    # based on adjacent words and baseline frequency
    def suggest(self, sentence, cursor_position, num_words):

        # these are the parts of the active sentence that come before and after the cursor
        before_cursor = sentence[0:cursor_position]
        after_cursor = sentence[cursor_position:]

        suggestions = {}

        # look at previous words in sentence, and all the words occurring after them
        for reach in range(1, self.hindsight+1):
            for n_gram_size in range(1, self.max_ngram_size+1):
                if len(before_cursor)+1 >= reach+n_gram_size:
                    end_of_n_gram = len(before_cursor)-reach
                    start_of_n_gram = end_of_n_gram - (n_gram_size-1)
                    previous_n_gram = " ".join(before_cursor[start_of_n_gram:end_of_n_gram+1])
                    after_previous = self.get_after(previous_n_gram, reach, num_words)
                    #print "after %s: %s" % (previous_n_gram, str(after_previous))
                    # crude function for privileging larger n-grams and closer contexts
                    weight = (10**n_gram_size)/(10**reach)
                    for tuple in after_previous:
                        key = tuple[0].string
                        value = tuple[1] * weight
                        if len(key.split(' ')) == 1:
                            if key not in suggestions:
                                suggestions[key] = value
                            else:
                                suggestions[key] += value

        for reach in range(1, self.foresight+1):
            for n_gram_size in range(1, self.max_ngram_size+1):
                if len(after_cursor)+1 >= reach+n_gram_size:
                    start_of_n_gram = reach - 1
                    end_of_n_gram = start_of_n_gram + (n_gram_size - 1)
                    next_n_gram = " ".join(after_cursor[start_of_n_gram:end_of_n_gram+1])
                    before_next = self.get_before(next_n_gram, reach, num_words)
                    #print "before %s: %s" % (next_n_gram.string, str(before_next))

                    # crude function for privileging larger n-grams and closer contexts
                    weight = (10**n_gram_size)/(10**reach)
                    for tuple in before_next:
                        key = tuple[0].string
                        value = tuple[1] * weight
                        if len(key.split(' ')) == 1:
                            if key not in suggestions:
                                suggestions[key] = value
                            else:
                                suggestions[key] += value

        baseline_weight = 0.00000001
        for key in self.tree:
            n_gram = self.tree[key]
            value = baseline_weight * n_gram.get_attribute(self.sort_attribute)
            if len(key.split(' ')) == 1:
                if key not in suggestions:
                    suggestions[key] = value
                else:
                    suggestions[key] += value

        suggestion_list = list(reversed(sorted(suggestions.items(), key=operator.itemgetter(1))))[0:num_words]

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


