import math

'''
Context: constructed using a dictionary and a list of words (the context in which we're typing),
this represents all the influences on the what list of words the program will suggest
'''

# used for weighing the inputs that determine the list of suggestions
class Context(object):
    default_context_settings = {'baseline_wt': .00000001, 'ngram_factor': 2, 'twoback_wt': 1}

    def __init__(self,D,prev_words,next_words,weights=default_context_settings):
        self.baseline = D
        self.baseline_wt = weights['baseline_wt']
        self.prev_ngrams = self.get_ngrams(D,prev_words)
        self.prev_ngrams_wt = self.set_ngram_wts(weights)
        self.twoback = self.get_twoback(D,prev_words)
        self.twoback_wt = weights['twoback_wt']
        #self.next_ngrams = self.set_oneforward(D,next_words)
        #self.set_twoforward = self.set_twoforward(D,next_words)


    def get_ngrams(self,D,prev_words):
        return self.ngramContinuations(D,prev_words)

    def set_ngram_wts(self,weights):
        ngram_wts = []
        for n in range(len(self.prev_ngrams)):
            ngram_wts.append(math.pow(weights['ngram_factor'],len(self.prev_ngrams)-n-1))
        return ngram_wts

    def get_twoback(self,D,prev_words):
        if len(prev_words) > 1 and prev_words[-2] in D:
            return D[prev_words[-2]].sub2
        else:
            return {}

    # TODO: implement these, which will enable backwards prediction (which words precede others)
    def get_oneforward(self,D,next_words):
        return

    def get_twoforward(self,D,next_words):
        return

    # given a list of recent words in the sentence and a dictionary, returns a list of dictionaries of words
    # that follow after all sizes of ngrams
    def ngramContinuations(self,D,recent_words):
        continuations = []
        for i in range(0,len(recent_words)):
            continuations.append(self.continuation(D,recent_words[i:]))
        return continuations

    # if the given sequence of words has occurred in the source, returns the dictionary of words that followed. otherwise returns false
    def continuation(self,D,sequence):
        if len(sequence)==0:
            return {}
        elif sequence[0] in D:
            if len(sequence) == 1:
                return D[sequence[0]].sub1
            elif len(sequence) > 1:
                restofsequence = sequence[1:]
                return self.continuation(D[sequence[0]].sub1,restofsequence)
        else:
            return{}
