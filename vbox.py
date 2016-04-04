#!/usr/bin/env python


'''


vbox.py: main script for predictive text writing

4/3/16: Some of the documentation, especially in the header, might be out-of-date. Please let me know if you find something glaring!

CLASSES

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


Voicebox: a collection of Voice objects and their associated weights

    attributes:
    voices: a dictionary of the various Voice objects in Voicebox

    methods:
    addVoice: adds a single Voice
    addTranscript: given a transcript where speakers are assigned to lines by SPEAKER: [line], breaks that script
    down into constituent speakers and adds a Voice for each
    makeDict: makes a dict and sets raw frequencies
    normalizeFreqs: processes a dict's frequencies into rates of occurrence
    sigScores: processes a dict's rates of occurrence into significance scores

Context: constructed using a dictionary and a list of words (the context in which we're typing),
this represents all the influences on the what list of words the program will suggest

TODO: Document the functions in this object.





'''


__author__ = 'jamiebrew'


###############################

# first one is weight to baseline dict, then to 1-back, then 2-back, then conjunction
default_wts = [0,0,1]
default_VSets = {'criterion':3,'vision':2,'ranktype':'norm','weights':default_wts,'loveOfSize':10}
default_VBSets = {'num_opts': 20,'direction':'forward','vision':2,
                 'showvalue':True,'showsource':True,'proportional_src':False}


import string
import operator
import os
import textwrap
import cPickle as pickle
import re

import math
import collections
clear = lambda: os.system('cls')

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
        print '\n',self.string
        print 'freq:',self.freq
        print 'norm:',self.norm
        print 'sig:',self.sig
        print

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
        print 'restricting %s to words that occur at least %s time(s)' % (name,self.criterion)
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
            print indent + word + ": " + str(D[word].norm)
            print indent + word + '.sub1:'
            self.printD(D[word].sub1,indent+"   ")
            print indent + word + '.sub2:'
            self.printD(D[word].sub2,indent+"   ")
            if indent == "":
                print '\n'

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

# main container class
class Voicebox(object):

    def __init__(self,settings=default_VBSets):
        self.voices = {}
        self.voiceWeights = {}
        self.num_opts = settings['num_opts']
        self.direction = settings['direction']
        self.vision = settings['vision']
        self.showvalue = settings['showvalue']
        self.showsource = settings['showsource']
        self.proportional_src = settings['proportional_src']

    # takes a file and adds one voice from it
    def addVoiceFromFile(self,filename,voicename=''):
        if voicename == '':
            voicename = filename
        voicenumber = str(len(self.voices)+1)+ ". "
        voicename = voicenumber + voicename
        D = self.makeDict('',filename)
        if filename[0:12] == 'transcripts/':        # cleans up the filename
            filename = filename[12:]
        self.voices[voicename] = Voice(filename,D)
        self.voiceWeights[voicename] = 1
        return self.voices[voicename]

    # adds a dictionary
    def addVoiceFromDict(self,D,voicename):
        voicenumber = str(len(self.voices)+1)+ ". "
        voicename = voicenumber + voicename
        self.voices[voicename] = Voice(voicename,D)
        self.voiceWeights[voicename] = 1
        return self.voices[voicename]

    # sets a specified voice to the desired weight
    def setVoiceWeight(self,voicename,weight):
        self.voiceWeights[voicename] = weight

    # takes a transcript, breaks it up by speaker and adds one voice for each speaker
    def addTranscript(self,tname,speakerlist):
        # splits file at ":" (so last word of each block is a speaker); pairs each line with last word before preceding colon

        path = 'texts/transcripts/%s' % tname
        f = open(path,"r")
        lines = f.read().lower().split(':')
        labeled_lines = []
        # associate each line with a speaker
        for i in range(1,len(lines)):
            labeled_lines.append((lines[i-1].split()[-1],lines[i].split()[0:-1]))

        # consolidate all lines by a given speaker into one line
        speakers = {}
        for line in labeled_lines:
            name = line[0]
            if name in speakerlist:
                if name in speakers:
                    speakers[name]+=line[1]
                else:
                    speakers[name] = line[1]
            else:
                # if the speakerlist has 'other' in it, then it consolidates all unclaimed lines into one
                if 'other' in speakerlist:
                    if 'other' in speakers:
                        speakers['other']+=line[1]
                    else:
                        speakers['other']=line[1]

        for name in speakers:
            # save file
            filename = 'transcripts/%s' % name
            path = 'texts/%s' % filename
            outfile = open(path,'w')
            toWrite = " ".join(speakers[name])
            outfile.write(toWrite)
            self.addVoiceFromFile(filename,filename[12:])

    # passed a string, makes a dictionary from a string. passed an empty string and a file, makes it from a file
    def makeDict(self,str,filename=''):
        if filename == '':
            sentences = str.split('.')
        else:
            print "Making dictionary from",filename+"..."
            path = 'texts/' + filename
            f = open(path,"r")
            sentences = f.read().split('.')

        # add every sentence in the source to the dictionary
        for s in range (0,len(sentences)):
            sentences[s] = sentences[s].strip('\n')
            sentences[s] = sentences[s].translate(string.maketrans("",""), string.punctuation)
            sentences[s] = sentences[s].lower()
            sentences[s] = sentences[s].split()

        D = {}
        # go through each sentence, add each word to the dictionary, incrementing length each time
        for s in sentences:
            for w in range(0,len(s)):
                self.addWord(D,s,w,self.vision)


        D = self.normalizeFreqs(D)
        D = self.sigScores(D,D)
        return D

    # uses word frequency information to
    def normalizeFreqs(self,D):
        if D == {}:
            return D
        #take the sum of all frequencies in D
        s = 0
        for w in D:
            s = s + D[w].freq
        # divide each frequency by the sum
        for w in D:
            D[w].set_sub1(self.normalizeFreqs(D[w].sub1))
            D[w].set_sub2(self.normalizeFreqs(D[w].sub2))
            D[w].set_norm(D[w].freq/float(s))
        return D

    # gives entries (and subentries) in D scores based on ratio to the baseline of SuperD
    def sigScores(self,D,superD):
        if D == {}:
            return D
        for w in D:
            D[w].set_sub1(self.sigScores(D[w].sub1,superD))
            D[w].set_sub2(self.sigScores(D[w].sub2,superD))
            D[w].set_sig((D[w].norm/superD[w].norm)*math.log(D[w].freq+1,10))
        return D

    # Add word at position pos in sentence s to dictionary D with vision v. Returns a dictionary.
    def addWord(self,D,s,pos,v):
        #extract string of word from the sentence
        word = s[pos]
        #base case. v is 0, so we're just returning D with the frequency of s[w] incremented, not altering subdictionaries
        if v <= 0:
            # increment the frequency if the word already exists
            if word in D:
                D[word].set_freq(D[word].freq+1)
            # otherwise, create a new entry in D
            else:
                D[word] = Word(word)
            return D

        # if v is greater than 0, we increment the frequency and ask for subdictionaries
        elif v>0:
            if word in D:
                newsub1 = D[word].sub1
                if pos < len(s)-1:
                    newsub1 = self.addWord(D[word].sub1,s,pos+1,v-1)

                newsub2 = D[word].sub2
                if v>1 and pos < len(s)-2:
                    newsub2 = self.addWord(D[word].sub2,s,pos+2,0)

                D[word].set_freq(D[word].freq+1)
                D[word].set_sub1(newsub1)
                D[word].set_sub2(newsub2)
                return D
            else:
                D[word] = Word(word)

                newsub1 = {}
                if pos < len(s)-1:
                    newsub1 = self.addWord(D[word].sub1,s,pos+1,v-1)

                newsub2 = {}
                if v>1 and pos < len(s)-2:
                    newsub2 = self.addWord(D[word].sub2,s,pos+2,0)


                D[word].set_sub1(newsub1)
                D[word].set_sub2(newsub2)
                return D

    # selects a single voice, setting the weights of all other voices to 0
    def useOneVoice(self,chosenVoiceName):
        for voicename in self.voiceWeights:
            self.voiceWeights[voicename] = 0
        self.voiceWeights[chosenVoiceName] = 1

    def getVoices(self):
        print "\ncurrent voicebox:"
        toReturn = {}
        tab = 15
        for voicename in sorted(self.voices):
            print voicename, ' '*(tab-len(voicename))+"(wt. "+str(self.voiceWeights[voicename])+")"

    # this takes a list of the most recent n words and returns a ranked list of options for the next word
    def getOptions(self,recent_words):
        aggregate = {}
        for v in self.voices:
            voice = self.voices[v]
            if self.voiceWeights!=0:
                contribution = voice.weighContexts(voice.activeD,recent_words)
                for w in contribution:
                    if w in aggregate:
                        aggregate[w][0] += contribution[w] * self.voiceWeights[v]
                        aggregate[w][1][v] = contribution[w] * self.voiceWeights[v]
                    else:
                        aggregate[w] = [0,{}]
                        aggregate[w][0] += contribution[w] * self.voiceWeights[v]
                        aggregate[w][1][v] = contribution[w] * self.voiceWeights[v]
                    # express the sources as proportions
                    if self.proportional_src:
                        for v in aggregate[w][1]:
                            aggregate[w][1][v] = aggregate[w][1][v]/sum(aggregate[w][1].values())

        toReturn = []
        for w in aggregate:
            toReturn.append([w,aggregate[w][0],aggregate[w][1]])

        ranked = sorted(toReturn, key=operator.itemgetter(1))
        optionList = list(reversed(ranked))[0:self.num_opts]            # returns as much of the top of the list as specified by num_opts
        self.options = optionList
        return optionList


    # returns a list of options of length num_opts
    def printOptions(self):
        print "\ntop words in voicebox:"
        for wordValSrc in self.options:
            tabs = 1
            tabsize = 25
            toPrint = wordValSrc[0]
            offset = " "* (tabs*tabsize - len(toPrint))
            tabs +=1
            if self.showvalue:
                val = float("{0:.4f}".format(wordValSrc[1]))
                toPrint += (offset + "(" + str(val) + ")")
                offset = " "* (tabs*tabsize - len(toPrint))
                tabs += 1
            if self.showsource:
                for v in self.voices:
                    if v in wordValSrc[2]:
                        val = float("{0:.4f}".format(wordValSrc[2][v]))
                    else:
                        val = 0.0000
                    toPrint += (offset +"("+ v + ": " + str(val) + ")")
                    offset = " "* (tabs*tabsize+5 - len(toPrint))
                    tabs +=1
            print toPrint

class Writer(object):

    voicebox = Voicebox()
    cursor = "|"

    def write(self,vb=voicebox):
        if not vb.voices:
            print "Cannot write with an empty Voicebox!"
            return

        self.chooseVoiceMenu(vb)

        scriptlog =[]
        cur = 0
        linelog = []
        hashtable = {}

        while 1:
            before = linelog[:cur]
            after = linelog[cur:]

            if vb.vision >= len(before):
                recent_words = before
            else:
                firstword = len(before) - vb.vision
                recent_words = before[firstword:]

            # hash check on this set of recent words
            if "".join(recent_words) in hashtable:
                options = hashtable["".join(recent_words)]
            else:
                options = vb.getOptions(recent_words)[0:vb.num_opts]
                hashtable["".join(recent_words)] = options

            self.printOptions(options)

            response = raw_input('Choose one\n')
            if response.isdigit():
                response = int(response)
                if response >= 1 and response <= vb.num_opts:
                    before += [options[response-1][0]]
                    linelog = before + after
                    cur += 1
                    print(self.voiceHeader(vb))
                    self.printLog(scriptlog+linelog,cur)
                elif response == 0:
                    scriptlog = scriptlog + linelog
                    print 'Final output: '
                    print ' '.join(scriptlog)
                    return scriptlog
                else:
                    print "Number out of range!"
                    self.printLog(scriptlog+linelog,cur)
            elif response == 'x':
                if len(before) == 0:
                    print "Cannot delete the start of the sentence!"
                else:
                    cur -= 1
                    del before[-1] # remove last element of current line
                    linelog = before + after
                self.printLog(scriptlog+linelog,cur)
            elif response == 'z':
                cur -= 1
                self.printLog(scriptlog+linelog,cur)
            elif response == 'c':
                if cur == len(linelog):
                    print "Already at end of sentence!"
                else:
                    cur += 1
                self.printLog(scriptlog+linelog,cur)
            elif response == '.' or response=='?':        # starts a new sentence
                before[-1] += response
                linelog = before + after
                scriptlog = scriptlog + linelog
                linelog = []
                self.printLog(scriptlog+linelog,cur)
            elif response in ['m','menu']:
                self.writing_menu(vb)
                self.printLog(scriptlog+linelog,cur)
            #elif re.compile('v\d',response):
            #    number = response[1]
            #    print "here"
            elif isinstance(response, str):
                before = before + [response]
                linelog = before + after
                cur += 1
                self.printLog(scriptlog+linelog,cur)
            else:
                print "Invalid input. Choose a number between 1 and " + str(vb.num_opts) + " or enter a word manually."
                self.printLog(scriptlog+linelog,cur)

    def voiceHeader(self,vb):
        headerString = "\nVOICES\n"
        for v in sorted(vb.voices):
            headerString += v + "     "
        headerString += "\n____________________"
        return headerString


    def printOptions(self,options):
        count = 1
        for o in options:
            print str(count)+':',o[0]#,(10-len(o[0]))*' ',o[1]
            count += 1

    def writing_menu(self,vb):
        top_menu_prompt = "Choose an option from below:" \
                      "\n 1. Select one voice." \
                      "\n 2. Assign custom weights." \
                      "\n 3. Change ranktypes." \
                      "\n 4. Get voice info." \
                      "\n 5. Add a voice." \
                      "\n 6. Save Voicebox" \
                      "\n 7. Load Voicebox" \
                      "\n 8. Exit menu.\n"

        response = raw_input(top_menu_prompt)
        if response.isdigit():
            response = int(response)

            if response == 1:
                self.chooseVoiceMenu(vb)

            elif response ==2:
                self.setWeightMenu(vb)

            elif response ==3:
                vb.getVoices()
                for v in sorted(vb.voices):
                    response = raw_input('Set ranktype for '+v+'\n')
                    if response in ['norm','freq','sig']:
                        vb.voices[v].ranktype = response
                        print v + ' ranktype set to ' + str(response)
                    else:
                        print "Please choose either 'norm' 'freq' or 'sig'"
                vb.getVoices()
            elif response ==4:
                print "not implemented"
                return
            elif response ==5:
                self.addVoiceMenu(vb)
            elif response == 6:
                path = 'saved/' + raw_input('Save as: ') + '.pkl'
                with open(path, 'wb') as output:
                    pickle.dump(vb, output, pickle.HIGHEST_PROTOCOL)
            elif response == 7:
                path = 'saved/' + raw_input('Load file: ') + '.pkl'
                with open(path, 'rb') as input:
                    p = pickle.load(input)
            elif response == 8:
                print "Returning to write"
                return

    # prints the log in a readable way
    def printLog(self,log,pos):
        before = log[:pos]
        after = log[pos:]
        toPrint = before + [self.cursor] + after
        print textwrap.fill(" ".join(toPrint),80)

    # offers several voice choices
    def chooseVoiceMenu(self,vb):
        print self.voiceHeader(vb)
        response = raw_input('Choose a voice by number from above. \nOr:\n'
                             '0 to use an equal mixture.\n'
                             'C to assign custom weights.\n')
        if response.isdigit():
            response = int(response)
            voicelist = sorted(vb.voices)
            print len(voicelist)
            if response == 0:
                print "Voices weighted equally!"
            elif response <= len(voicelist):
                voicename = voicelist[response-1]
                vb.useOneVoice(voicename)
                print voicename + ' selected!'
        elif response == 'C':
            self.setWeightMenu(vb)
        else:
            print 'Invalid response! Type a number in range.'

    def setWeightMenu(self,vb):
        vb.getVoices()
        for v in sorted(vb.voices):
            response = raw_input('Set weight for '+v+'\n')
            if response.isdigit():
                response = int(response)
                vb.voiceWeights[v] = response
                print v + ' weight set to ' + str(response)
            else:
                print "Please type a number!"
        vb.getVoices()

    def addVoiceMenu(self,vb):
        print self.voiceHeader(vb)
        import glob
        textfiles = glob.glob('texts/*')
        count = 1
        for filename in textfiles:
            print str(count) + ": " + filename[6:]
            count+=1
        response = raw_input('Choose a file by number from above.')
        if response.isdigit():
            response = int(response)
            vb.addVoiceFromFile(textfiles[response-1][6:])




w = Writer()
vb = Voicebox()
vb.addVoiceFromFile('howl')
vb.addVoiceFromFile('poorrichard')
w.write(vb)
