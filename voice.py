from __future__ import print_function

from word import Word
from context import Context

'''
Voice: represents data from a given corpus. initialize it by passing in a dictionary

    attributes:

    D: the dictionary constructed from the source on the first pass

    activeD: a pruned version of D containing only words that occur a certain number of times

    VoiceSettings: determines the pruning criterion for this voice and the way in which its words get ranked
    (i.e., by normalized frequency, raw frequency or significance score)

    methods:

    restrict(dictionary,list): given a list of words, takes a dictionary and returns a dictionary with only
    matching words

    atLeast(dictionary,int): finds all the words in a dictionary that pass a frequency criterion, passes this
    list to restrict()
'''

# first one is weight to baseline dict, then to 1-back, then 2-back, then conjunction
default_wts = [0,0,1]
default_VSets = {'criterion':3,'vision':2,'ranktype':'norm','weights':default_wts,'loveOfSize':10}

# contains information about a source stored as a dictionary of all distinct words
class Voice(object):
    def __init__(self,name,dict,number=1,criterion=1,settings=default_VSets):
        self.criterion = criterion
        self.vision = settings['vision']
        self.ranktype = settings['ranktype']
        self.weights = settings['weights']
        self.loveOfSize = settings['loveOfSize']    # defines how much this voice privileges larger ngrams

        self.name = name
        self.D = dict
        self.activeD = self.atLeast(dict,name,self.criterion)


    # restricts D to the list of words that occur n times in D
    def atLeast(self,D,name,n):
        print('restricting %s to words that occur at least %s time(s)' % (name,self.criterion))
        commonWords = []
        for word in self.D:
            if self.D[word].freq >= n:
                commonWords = commonWords + [word]
        return self.restrict(D,commonWords)

    # restricts the dictionary to a specified list of words
    def restrict(self,D,wordlist):
        if D == {}:
            return D
        else:
            restrictedD = {}
            for w in D:
                if w in wordlist:
                    restrictedD[w] = D[w]
                    restrictedD[w].set_sub1(self.restrict(D[w].sub1,wordlist))
                    restrictedD[w].set_sub2(self.restrict(D[w].sub2,wordlist))
            return restrictedD

    # expresses the summed scores in an aggregate dictionary as a proportion of the total
    def normScores(self,aggregate_D):
        #take the sum of all frequencies in D
        summed_freqs = 0
        summed_norms = 0
        summed_sigscores = 0
        for w in aggregate_D:
            summed_freqs += aggregate_D[w].freq
            summed_norms += aggregate_D[w].norm
            summed_sigscores += aggregate_D[w].sig

        normalized_D = {}
        for w in aggregate_D:
            normalized_D[w] = Word(w)
            normalized_D[w].set_sub1(aggregate_D[w].sub1)
            normalized_D[w].set_sub2(aggregate_D[w].sub2)
            normalized_D[w].set_freq(aggregate_D[w].freq/float(summed_freqs))
            normalized_D[w].set_norm(aggregate_D[w].norm/float(summed_norms))
            normalized_D[w].set_sig(aggregate_D[w].sig/float(summed_sigscores))

        return normalized_D

    # prints the whole dictionary. Is passed a string of several spaces as an indent
    def printD(self,D,indent):
        for x in reversed(sorted(D.items(), key=operator.itemgetter(1))):
            word = x[0]
            print(indent + word + ": " + str(D[word].norm))
            print(indent + word + '.sub1:')
            self.printD(D[word].sub1,indent+"   ")
            print(indent + word + '.sub2:')
            self.printD(D[word].sub2,indent+"   ")
            if indent == "":
                print('\n')

    # returns a dictionary of words with the weights consolidated from all ngrams derived from recent_words, plus baseline
    def weighContexts(self,D,recent_words,ranktype=''):

        # if no ranktype specified, go with the default
        if ranktype == '':
            ranktype = self.ranktype

        C = Context(D,recent_words,'')

        # locus of summing of weights
        aggregated = {}

        # include baseline dictionary in aggregated
        d = C.baseline
        wt = C.baseline_wt
        for w in d:
            aggregated[w] = Word(w)
            aggregated[w].freq += wt * d[w].freq
            aggregated[w].norm += wt * d[w].norm
            aggregated[w].sig += wt * d[w].sig

        # include ngrams of all lengths in aggregated
        for n in range(0,len(C.prev_ngrams)):
            d = C.prev_ngrams[n]
            wt = C.prev_ngrams_wt[n]
            for w in d:
                aggregated[w].freq += wt * d[w].freq
                aggregated[w].norm += wt * d[w].norm
                aggregated[w].sig += wt * d[w].sig

        # include two-back
        d = C.twoback
        wt = C.twoback_wt
        for w in d:
            aggregated[w].freq += wt * d[w].freq
            aggregated[w].norm += wt * d[w].norm
            aggregated[w].sig += wt * d[w].sig

        normed = self.normScores(aggregated)

        toReturn = {}
        # choose the appropriate scoring metric (could add more scoring metrics here)
        for w in normed:
            if ranktype == 'norm':
                toReturn[w] = normed[w].norm
            elif ranktype == 'sig':
                toReturn[w] = normed[w].sig
            elif ranktype == 'freq':
                toReturn[w] = normed[w].freq
        return toReturn
