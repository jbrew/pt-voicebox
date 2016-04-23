#!/usr/bin/env python

from writer import Writer
from vbox import Voicebox

'''
vbox.py: main script for predictive text writing

4/3/16: Some of the documentation, especially in the header, might be out-of-date. Please let me know if you find something glaring!
'''

w = Writer()
vb = Voicebox()
vb.addVoiceFromFile('howl')
vb.addVoiceFromFile('poorrichard')
w.write(vb)
