__author__ = 'jamiebrew'

import operator

# information about a unique string within a corpus
class Ngram(object):

    def __init__(self, string):
        self.string = string
        self.count = 1                  # how many times this ngram occurs
        self.after = []                 # list of dictionaries
        self.before = []                # list of dictionaries
        self.frequency = 0              # normalized rate of occurrence
        self.sig_score = 0              # significance score
        self.rhymes = {}

    def __str__(self):
        return self.string+"\ncount: "+str(self.count)+"\nfreq: "+str(self.frequency)+"\nsig: "+str(self.sig_score)+'\n'

    def __repr__(self):
        return self.string

    def __len__(self):
        return len(self.string)

    # returns top n words occuring distance after this ngram
    def get_after(self, distance=1, n=20, sort_attribute="count"):
        return self._get_ngram_and_attribute(distance, n, sort_attribute, True)

    # returns top n words occuring distance before this ngram
    def get_before(self, distance=1, n=20, sort_attribute="count"):
        return self._get_ngram_and_attribute(distance, n, sort_attribute, False)

    def _get_ngram_and_attribute(self, distance, n, sort_attribute, is_after):
        distance -= 1
        dictionary = self.after[distance] if is_after else self.before[distance]

        return list(
            reversed(
                sorted(
                    map(
                        lambda (string, ngram): (
                            string,
                            getattr(ngram, sort_attribute)
                        ),
                        dictionary.iteritems()
                    ),
                    key=lambda tuple: tuple[1]
                )
            )
        )[0:n]
