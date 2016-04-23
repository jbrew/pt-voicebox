from __future__ import print_function
import textwrap
try:
    import cPickle as pickle
except ImportError:
    import pickle
import re

from vbox import Voicebox

class Writer(object):

    voicebox = Voicebox()
    cursor = "|"

    def write(self,vb=voicebox):
        if not vb.voices:
            print("Cannot write with an empty Voicebox!")
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

            try:
                response = raw_input('Choose one\n')
            except NameError:
                response = input('Choose one\n')
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
                    print('Final output: ')
                    print(' '.join(scriptlog))
                    return scriptlog
                else:
                    print("Number out of range!")
                    self.printLog(scriptlog+linelog,cur)
            elif response == 'x':
                if len(before) == 0:
                    print("Cannot delete the start of the sentence!")
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
                    print("Already at end of sentence!")
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
                print("Invalid input. Choose a number between 1 and " + str(vb.num_opts) + " or enter a word manually.")
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
            print(str(count)+':',o[0])  # ,(10-len(o[0]))*' ',o[1]
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

        try:
            response = raw_input(top_menu_prompt)
        except NameError:
            response = input(top_menu_prompt)
        if response.isdigit():
            response = int(response)

            if response == 1:
                self.chooseVoiceMenu(vb)

            elif response ==2:
                self.setWeightMenu(vb)

            elif response ==3:
                vb.getVoices()
                for v in sorted(vb.voices):
                    try:
                        response = raw_input('Set ranktype for '+v+'\n')
                    except NameError:
                        response = input('Set ranktype for '+v+'\n')
                    if response in ['norm','freq','sig']:
                        vb.voices[v].ranktype = response
                        print(v + ' ranktype set to ' + str(response))
                    else:
                        print("Please choose either 'norm' 'freq' or 'sig'")
                vb.getVoices()
            elif response ==4:
                print("not implemented")
                return
            elif response ==5:
                self.addVoiceMenu(vb)
            elif response == 6:
                try:
                    path = 'saved/' + raw_input('Save as: ')
                except NameError:
                    path = 'saved/' + input('Save as: ') + '.pkl'
                with open(path, 'wb') as output:
                    pickle.dump(vb, output, pickle.HIGHEST_PROTOCOL)
            elif response == 7:
                try:
                    path = 'saved/' + raw_input('Load file: ')
                except NameError:
                    path = 'saved/' + input('Load file: ') + '.pkl'
                with open(path, 'rb') as i:
                    p = pickle.load(i)
            elif response == 8:
                print("Returning to write")
                return

    # prints the log in a readable way
    def printLog(self,log,pos):
        before = log[:pos]
        after = log[pos:]
        toPrint = before + [self.cursor] + after
        print(textwrap.fill(" ".join(toPrint),80))

    # offers several voice choices
    def chooseVoiceMenu(self,vb):
        print(self.voiceHeader(vb))
        try:
            response = raw_input('Choose a voice by number from above. \nOr:\n'
                                 '0 to use an equal mixture.\n'
                                 'C to assign custom weights.\n')
        except NameError:
            response = input('Choose a voice by number from above. \nOr:\n'
                             '0 to use an equal mixture.\n'
                             'C to assign custom weights.\n')
        if response.isdigit():
            response = int(response)
            voicelist = sorted(vb.voices)
            print(len(voicelist))
            if response == 0:
                print("Voices weighted equally!")
            elif response <= len(voicelist):
                voicename = voicelist[response-1]
                vb.useOneVoice(voicename)
                print(voicename + ' selected!')
        elif response == 'C':
            self.setWeightMenu(vb)
        else:
            print('Invalid response! Type a number in range.')

    def setWeightMenu(self,vb):
        vb.getVoices()
        for v in sorted(vb.voices):
            try:
                response = raw_input('Set weight for '+v+'\n')
            except NameError:
                response = input('Set weight for '+v+'\n')
            if response.isdigit():
                response = int(response)
                vb.voiceWeights[v] = response
                print(v + ' weight set to ' + str(response))
            else:
                print("Please type a number!")
        vb.getVoices()

    def addVoiceMenu(self,vb):
        print(self.voiceHeader(vb))
        import glob
        textfiles = glob.glob('texts/*')
        count = 1
        for filename in textfiles:
            print(str(count) + ": " + filename[6:])
            count+=1
        try:
            response = raw_input('Choose a file by number from above.')
        except NameError:
            response = input('Choose a file by number from above.')
        if response.isdigit():
            response = int(response)
            vb.addVoiceFromFile(textfiles[response-1][6:])
