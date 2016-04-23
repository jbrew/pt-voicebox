from __future__ import print_function
import string
import operator
import os
import math
import collections
clear = lambda: os.system('cls')

from voice import Voice
from word import Word

__author__ = 'jamiebrew'

'''
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

TODO: Document the functions in this object.
'''

default_VBSets = {'num_opts': 20,'direction':'forward','vision':2,
                 'showvalue':True,'showsource':True,'proportional_src':False}

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
            print("Making dictionary from",filename+"...")
            path = 'texts/' + filename
            f = open(path,"r")
            sentences = f.read().split('.')

        # add every sentence in the source to the dictionary
        for s in range (0,len(sentences)):
            sentences[s] = sentences[s].strip('\n')
            try:
                sentences[s] = sentences[s].translate(string.maketrans("",""), string.punctuation)
            except AttributeError:
                sentences[s] = sentences[s].translate({i: "" for i in string.punctuation})
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
        print("\ncurrent voicebox:")
        toReturn = {}
        tab = 15
        for voicename in sorted(self.voices):
            print(voicename, ' '*(tab-len(voicename))+"(wt. "+str(self.voiceWeights[voicename])+")")

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
        print("\ntop words in voicebox:")
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
            print(toPrint)
