#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'jamiebrew'

import os
import corpus
import operator
import textwrap
import random
import re
import voice
import pickler
#import urllib2
#from bs4 import BeautifulSoup
#import unicodedata

"""
input loop for writing with a corpus or set of corpora


WRITING CONTROLS:

[option #]:     choose option
x:              delete
. or ? or !:    end sentence
z:              move cursor left
c:              move cursor right
r:              choose random word (weighted)
v[voice #]:     change voice
add:            add voice
set:            set corpus weights for this voice
info:           toggle extra info
dynamic:        toggle dynamic writing
save:           save session
load:           load session
[other word]:   insert word
0:              yield output


"""
class Voicebox(object):

    def __init__(self):
        self.more_info = False
        self.dynamic = False
        self.mode_list = ['frequency', 'sigscore', 'count']
        self.mode = 'frequency'
        #self.spanish_to_english = False
        self.num_options = 20

        load_prev = raw_input('Load previous session? y/n\n')
        if load_prev != 'n':
            loaded_voicebox = self.load_session()               # unpickles a previously-saved object
            self.cursor = loaded_voicebox.cursor
            self.cursor_position = loaded_voicebox.cursor_position
            self.voices = loaded_voicebox.voices
            self.active_voice = loaded_voicebox.active_voice
            self.log = loaded_voicebox.log
        else:
            self.cursor = "|"
            self.cursor_position = 0
            self.voices = {}
            self.load_voices()
            self.active_voice = self.choose_voice()
            self.log = []

    def header(self):
        headerString = "\nVOICES\n"
        vnum = 1
        for voice in sorted(self.voices):
            v = self.voices[voice]
            headerString += 'v%s. %s\n' % (str(vnum), v.name)
            vnum+=1
            source_num = 1
            if len(v.weighted_corpora) > 1:         # only print the component sources of voices with more than one
                for corpus in sorted(v.weighted_corpora):
                    c, wt = v.weighted_corpora[corpus]
                    headerString += '\ts%s. %s, weight %s\n' % (str(source_num), c.name, wt)
                    source_num +=1
        headerString += "\n____________________"
        return headerString

    def write(self):
        sentence = ['START_SENTENCE']
        self.cursor_position = 1
        voice_name = self.active_voice.name.upper()
        self.log += [voice_name + ':']
        while 1:
            words_before = sentence[0:self.cursor_position]
            words_after = sentence[self.cursor_position:]
            suggestions = self.active_voice.suggest(sentence, self.cursor_position, self.num_options)
            print self.header()
            print textwrap.fill(" ".join(self.log + words_before[1:] + [self.cursor] + words_after),80)
            self.display_suggestions(suggestions)

            #if self.spanish_to_english:
            #    print words_before[-1]+ ": " + self.to_english(words_before[-1]).encode('utf-8').strip()
            #    self.spanish_to_english = False

            input = raw_input('What now?\n')
            
            try:
                input = int(input)
                if input in range(1, len(suggestions)+1):
                    choice = self.take_suggestion(suggestions, input)
                    next_word = choice[0]
                    score_tree = choice[1][1]
                    words_before.append(next_word)
                    sentence = words_before + words_after
                    if self.dynamic:
                        self.update_weights(self.active_voice, score_tree, .1)
                    self.cursor_position += 1
                elif input == 0:
                    self.log = self.log + sentence
                    self.log.remove('START_SENTENCE')
                    print " ".join(self.log)
                    return
                else:
                    print "That's out of range!"
            except:
                pass
                if input == 'z':
                    self.cursor_position -= 1
                elif input == 'c':
                    self.cursor_position +=1
                elif input == 'x':
                    self.delete_word(words_before)
                    self.cursor_position -= 1
                    sentence = words_before+words_after
                elif input == 'r':
                    next_word = self.weighted_random_choice(suggestions)
                    words_before.append(next_word)
                    sentence = words_before + words_after
                    self.cursor_position += 1
                #elif input == 't':
                #    self.spanish_to_english = True
                elif input == 'info':
                    self.toggle_info()
                elif input == 'dynamic':
                    self.toggle_dynamic()
                elif input == 'add':
                    self.add_voice()
                elif input == 'set':
                    self.set_weights(self.active_voice)
                elif re.compile('v[0-9]').search(input): # switch to different corpus
                    voice_num = input[1:]
                    voice_keys = sorted(self.voices.keys())
                    chosen_voice_name = voice_keys[int(voice_num) - 1]
                    self.active_voice = self.voices[chosen_voice_name]
                    print '%s chosen!' % chosen_voice_name
                    finished_sentence = self.finish_sentence(words_before, words_after, '.', '\n\n')
                    self.log = self.log + [finished_sentence] + [chosen_voice_name.upper() + ':']
                    sentence = ['START_SENTENCE']
                elif re.compile('o[0-9]').search(input): # change number of options
                    number_chosen = input[1:]
                    self.num_options = int(number_chosen)
                    print 'Now writing with %s options!' % number_chosen
                elif input in ['.', '?','!']:
                    finished_sentence = self.finish_sentence(words_before, words_after, input)
                    self.log = self.log + [finished_sentence]
                    sentence = ['START_SENTENCE']
                    self.cursor_position = 1
                elif input == 'save':
                    self.save_session()
                elif input == 'load':
                    self.load_session()
                elif isinstance(input, str) and len(input.strip()) > 0:
                    words_before.append(input)
                    sentence = words_before + words_after
                    self.cursor_position += 1
                else:
                    print "Invalid input."

    # toggles whether weights to sources in the current voice adjust automatically
    def toggle_dynamic(self):
        self.dynamic = not self.dynamic
        if self.dynamic:
            print "Dynamic weight adjustment on!"
        else:
            print "Dynamic weight adjustment off!"

    # toggles whether to show information about scores (and their decomposition by source)
    def toggle_info(self):
        self.more_info = not self.more_info
        if self.more_info:
            print "More info on!"
        else:
            print "More info off!"

    def set_mode(self):
        for i in range(len(self.mode_list)):
            print "%s %s" % (i + 1, self.mode_list[i])
        choice = raw_input('Enter the number of the session you want to load:\n')
        self.mode = self.mode_list[int(choice) - 1]

    # saves all information about the current session
    def save_session(self):
        path = 'saved/%s.pkl' % raw_input("Choose save name:\n")
        pickler.save_object(self, path)
        print "Saved voicebox to %s!" % path

    # prompts choice of session to load, then loads it.
    def load_session(self):
        sessions = os.listdir('saved')
        for i in range(len(sessions)):
            print "%s %s" % (i + 1, sessions[i])
        choice = raw_input('Enter the number of the session you want to load:\n')
        session_name = sessions[int(choice) - 1]
        path = 'saved/%s' % session_name
        return pickler.loadobject(path)

    # given a chosen word and a tree of scores assigned to it by different sources, updates the weights of those sources
    # according to whether they exceeded or fell short of their expected contribution to the suggestion
    def update_weights(self, v, score_tree, delta):
        total_score = sum(score_tree.values())
        for key in v.weighted_corpora:
            corp, wt = v.weighted_corpora[key]
            expected_share = wt/1
            if key in score_tree:
                sub_score = score_tree[key]
            else:
                sub_score = 0
            actual_share = sub_score / total_score
            performance_relative_to_expectation = actual_share - expected_share
            v.weighted_corpora[corp.name][1] += performance_relative_to_expectation * delta

    # prompts user to set weights for each corpus in a given voice
    def set_weights(self, v):
        for key in v.weighted_corpora:
            corpus_name = v.weighted_corpora[key][0].name
            corpus_weight_prompt = 'Enter the weight for %s:\n' % corpus_name
            corpus_weight = float(raw_input(corpus_weight_prompt))
            v.weighted_corpora[key][1] = corpus_weight
        v.normalize_weights()

    # random choice without weight bias
    def flat_random_choice(self, suggestions):
        return random.randint(1, len(suggestions))

    # returns a word from the suggestion list; choice weighted according to scores
    def weighted_random_choice(self, suggestions):
        total = sum(score_info[0] for word, score_info in suggestions)
        r = random.uniform(0,total)
        upto = 0
        for word, score_info in suggestions:
            if upto + score_info[0] >= r:
                return word
            upto += score_info[0]
        assert False, "Shouldn't get here"

    # deletes word before the cursor from sentence
    def delete_word(self, before):
        if len(before) == 1:
            print "Cannot delete the start of the sentence!"
        else:
            del before[-1] # remove last element of current line
    #
    def finish_sentence(self, before, after, delimiter, line_break = ''):
        sentence = before[1:] + after
        if len(sentence) > 0:
            sentence[-1] += delimiter
        sentence += line_break
        return " ".join(sentence)

    def load_voices(self):
        if raw_input('Load from transcript? y/n\n') in ['y','yes']:
            self.load_voices_from_transcript()
        else:
            add_another_voice = ''
            while add_another_voice != 'n':
                self.add_voice()
                add_another_voice = raw_input('Add more? y/n\n')

    # asks you to choose corpora from files in 'texts', then adds a voice with those corpora
    def add_voice(self):
        new_voice = voice.Voice({})     # creates new voice with no name and empty tree of corpora
        texts = os.listdir('texts')
        add_another_corpus = ''
        while add_another_corpus != 'n':
            for i in range(len(texts)):
                print "%s %s" % (i + 1, texts[i])
            choice = raw_input('Enter the number of the corpus you want to load:\n')
            corpus_name = texts[int(choice) - 1]
            path = 'texts/%s' % corpus_name
            f = open(path, 'r')
            text = f.read()
            corpus_weight_prompt = 'Enter the weight for %s:\n' % corpus_name
            corpus_weight = float(raw_input(corpus_weight_prompt))
            new_voice.add_corpus(corpus.Corpus(text, corpus_name), corpus_weight)
            texts.remove(corpus_name)
            add_another_corpus = raw_input('Add another corpus to this voice? y/n\n')
        voicename = raw_input('Name this voice:\n')
        new_voice.name = voicename
        new_voice.normalize_weights()
        self.voices[voicename] = new_voice

    # asks user to specify a transcript and number of characters, and makes separate voices for that number of
    # the most represented characters in the transcript
    def load_voices_from_transcript(self):
        transcripts = os.listdir('texts/transcripts')
        for i in range(len(transcripts)):
            print "%s %s" % (i + 1, transcripts[i])
        choice = raw_input('Enter the number of the transcript you want to load:\n')
        transcript_name = transcripts[int(choice) - 1]
        number = int(raw_input('Enter the number of voices to load:\n'))
        for charname, size in self.biggest_characters(transcript_name, number):
            print charname
            path = 'texts/transcripts/%s/%s' % (transcript_name, charname)
            source_text = file(path).read()
            corpus_name = charname
            weighted_corpora = {}
            weighted_corpora[charname] = [corpus.Corpus(source_text, corpus_name),1]
            self.voices[charname] = voice.Voice(weighted_corpora, charname)

    # retrieves a list of the top 20 largest character text files in a transcript folder
    def biggest_characters(self, tname, number):
        size_by_name = {}
        tpath = 'texts/transcripts/%s' % tname
        for cname in os.listdir(tpath):
            cpath = '%s/%s' % (tpath, cname)
            size_by_name[cname] = len(file(cpath).read().split())
        sorted_chars = list(reversed(sorted(size_by_name.items(), key=operator.itemgetter(1))))
        return sorted_chars[0:number]

    # offers several voice choices, returns a voice
    def choose_voice(self):
        voice_keys = sorted(self.voices.keys())
        print "VOICES:"
        for i in range(len(voice_keys)):
            print "%s: %s" % (i + 1, voice_keys[i])
        choice = raw_input('Choose a voice to write with...\n')
        self.active_voice = self.voices[voice_keys[int(choice) - 1]]
        return self.active_voice

    def display_suggestions(self, suggestions):
        suggestion_string = '\n'
        for i in range(len(suggestions)):
            total_score = format(sum(suggestions[i][1][1].values()),'g')
            info_string = "%s: %s" % (i + 1, str(suggestions[i][0]))
            if self.more_info:
                info_string += '\t' + str(total_score)
            suggestion_string += info_string

            score_tree = suggestions[i][1][1]
            if self.more_info:
                suggestion_string += '\t\t'
                for key in score_tree:
                    score = format(score_tree[key], 'g')
                    suggestion_string += '\t%s: %s' % (key, score)
            suggestion_string += '\n'
        print suggestion_string

    def take_suggestion(self, suggestions, input):
        return suggestions[int(input) - 1]

    """
    # These functions are for looking up the definitions of unfamiliar words.
    # They require installing the HTML parsing tool Beautiful Soup, so I've commented them out.
    # If you have bs4, feel free to try them!

    def to_english(self, word):
        search_term = urllib2.quote(word)
        search_url = 'http://www.spanishdict.com/translate/%s' % search_term
        print search_url
        page = urllib2.urlopen(search_url).read()
        print len(page)
        soup = BeautifulSoup(page.decode('utf-8','ignore'), "html.parser")
        foo = soup.findAll(class_="dictionary-neodict-translation-translation")
        print len(foo)
        to_return = []
        for x in foo:
            to_return.append(x.get_text())
        return ", ".join(to_return)

    def to_english2(self, word):
        search_url = 'https://translate.google.com/#es/en/%s' % word
        page = urllib2.urlopen(search_url).read()
        soup = BeautifulSoup(page.decode('utf-8','ignore'), "html.parser")
        foo = soup.findAll(class_="dictionary-neodict-translation-translation")
        """

def main():
    vb = Voicebox()
    vb.write()

main()