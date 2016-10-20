from __future__ import absolute_import
__author__ = 'jamiebrew'

import operator

# keeps a dictionary of sources with associated weights
class Voice(object):

    def __init__(self, weighted_corpora, name = 'no_name'):
        self.name = name
        self.weighted_corpora = weighted_corpora

    # aggregates the suggestion lists of all constituent corpora in this voice, prints the top num_words from this list
    def suggest(self, sentence, cursor_position, num_words):
        suggestions = {}
        for key in self.weighted_corpora:
            corp, weight = self.weighted_corpora[key]
            if not weight == 0:
                contributed_suggestions = corp.suggest(sentence, cursor_position, num_words)
                for word, score in contributed_suggestions:
                    if word not in suggestions:
                        suggestions[word] = [0, {}]
                        suggestions[word][0] += score * weight
                        suggestions[word][1][corp.name] = score
                    else:
                        suggestions[word][0] += score * weight
                        suggestions[word][1][corp.name] = score
        suggestions = list(reversed(sorted(list(suggestions.items()), key=operator.itemgetter(1))))[0:num_words]
        return suggestions[0:num_words]

    # adds a corpus to this voice
    def add_corpus(self, corp, weight):
        self.weighted_corpora[corp.name] = [corp, weight]

    # proportionally adjusts the weights to different corpora such that they sum to 1
    def normalize_weights(self):
        total_weight = 0
        for key in self.weighted_corpora:
            total_weight += self.weighted_corpora[key][1]
        for key in self.weighted_corpora:
            self.weighted_corpora[key][1] = self.weighted_corpora[key][1] / total_weight