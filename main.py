#!/usr/bin/env python

import os
from writer import Writer
from vbox import Voicebox

'''
main.py: main script for predictive text writing

4/3/16: Some of the documentation, especially in the header, might be out-of-date. Please let me know if you find something glaring!
'''

w = Writer()
vb = Voicebox()

source_texts = os.listdir('texts')

add_another = ''
choices = []

while add_another != 'n':
  for i in range(len(source_texts)):
    print "%s %s" % (i + 1, source_texts[i])

  choice = raw_input('Enter the number of the voice you want to load:\n')

  source = source_texts[int(choice) - 1]
  choices.append(source)
  source_texts.remove(source)
  print "added %s!" % source

  add_another = raw_input('Load another voice? y/n\n')

for source_text in choices:
  vb.addVoiceFromFile(source_text)

rand_word= raw_input('Use random words? y/n\n')

w.set_rand(rand_word)
w.write(vb)
