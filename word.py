from __future__ import print_function

'''
Word: this construct replaces the dictionary entries from the previous script.
you initialize a word by passing in a string

    attributes:

    name: the word itself

    freq: the raw frequency of that word within its dictionary

    sub1: dictionary of words that follow this word

    sub2: dicionary of words that come two after this word

    norm: normalized frequency of the word (chance of occurring)

    sig: the significance score of the word, which is how much the frequency in this dictionary
    exceeds baseline frequency

    methods:

    There's a print method and there are methods to set each of the attributes

    NOTE ON SIGNIFICANCE SCORE:
    I introduced this to avoid a problem with large dictionaries: the top suggestions tend to be extremely common words, even given
    specific contexts. If the previous two words are 'jack the' then one continuation you'd like to have is 'ripper.'
    but if you go strictly by rate of occurrence, then phrases like 'jack, the thing' [is] and [i gave] 'jack the keys'
    are going to overwhelm 'jack the ripper'

    To solve this, significance score tries to index how much the context in question boosts a word's frequency
    over baseline. This may be what you would call a Bayesian approach:

    sig = P(w|context)/P(w)

    So if 'ripper' occurs 1 percent of the time after 'jack the' but only .0000001 percent of the time overall,
    it gets a huge sigscore. meanwhile, 'thing' might occur 2 percent of the time after 'jack the' but .05 percent
    of the time overall, giving it a more modest sigscore

    To avoid giving huge sigscores to sequences that occur just once or twice, I've mulitplied the sigscore by
    the log of the frequency as a way of discounting those little blips we should probably make the base of that
    log function into a parameter so we can adjust how much the program privileges sequences with high frequencies.
'''

# stores all the information about a word within a dictionary
class Word(object):

    def __init__(self,string,freq=1):
        self.string = string
        self.freq = freq
        self.sub1 = {}
        self.sub2 = {}
        self.norm = 0
        self.sig = 0

    def set_freq(self,new_freq):
        self.freq = new_freq

    def set_norm(self,new_norm):
        self.norm = new_norm

    def set_sig(self,new_sig):
        self.sig = new_sig

    def set_sub1(self,new_sub1):
        self.sub1 = new_sub1

    def set_sub2(self,new_sub2):
        self.sub2 = new_sub2

    def printWord(self):
        print('\n',self.string)
        print('freq:',self.freq)
        print('norm:',self.norm)
        print('sig:',self.sig)
        print()
