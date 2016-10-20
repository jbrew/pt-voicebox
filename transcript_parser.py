from __future__ import absolute_import
from __future__ import print_function
from six.moves import range
__author__ = 'jamiebrew'

import os
import string
import operator

"""
Takes a transcript formatted as follows, with newlines separating lines, and without paragraph breaks in the middle of
lines. (this is how transcripts are formatted on genius.com)

Pulls the transcript from 'raw_transcripts/name]' and saves them to 'texts/transcripts/[name]'

[[
CHARACTER: I am saying a line and I am using a VARIety of CapITALIzations and   spacing    patterns

OTHER CHARACTER: Okay...

Here are some stage directions in a separate paragraph that does not contain a colon. The characters are kissing
each other.

]]

Feeds these into separate text files, each containing the collection of lines spoken by a particular character,
each named after the character. Also creates a file called "stage directions" that has all of the lines that did
not seem to be attributed to a character.

NOTES:

Assumes that lines are attributed using a colon.

Assumes that colons do not appear in stage direction paragraphs.

Does not know about alternate names for the same character. WILLY LOMAN and WILLY will be fed into different files.
Likewise, WILLY (to himself) will be fed into a different file from WILLY.

"""


# parser for game of thrones transcripts
class transcript_parser(object):

    def parseTranscript(self, tname):
            path = 'raw_transcripts/%s' % tname
            f = open(path,"r")
            # splits file at ":" (so last word of each block is a speaker); pairs each line with last word before preceding colon
            lines = f.read().lower().split('\n')
            for line in lines:
                line = line.strip('\n')
            labeled_lines = []

            # associate each line with a speaker
            for i in range(1,len(lines)):
                if ':' in lines[i]:
                    pair = lines[i].split(':', 1)   # splits only at first instance of ':'
                    labeled_lines.append(pair)
                else:
                    labeled_lines.append(['stage directions',lines[i]])

            # consolidate all lines by a given speaker into one line
            speakers = {}
            for line in labeled_lines:
                if six.PY2:
                    name = line[0].split(string.punctuation)[0].translate(string.maketrans("",""),'/')
                elif six.PY3:
                    name = line[0].split(string.punctuation)[0].translate(str.maketrans({'/': None})
                else:
                    raise NotImplementedError("expected either PY2 or PY3")

                if name in speakers:
                    speakers[name]+=line[1]
                else:
                    speakers[name] = line[1]

            for name in speakers:
                # save file
                dirpath = 'texts/transcripts/%s' % tname
                if not os.path.isdir(dirpath):
                    os.mkdir(dirpath)
                path = 'texts/transcripts/%s/%s' % (tname,name)

                outfile = open(path,'w')
                toWrite = speakers[name]
                outfile.write(toWrite)


    def biggest_characters(self, tname, number):
        size_by_name = {}
        tpath = 'texts/transcripts/%s' % tname
        for cname in os.listdir(tpath):
            cpath = '%s/%s' % (tpath, cname)
            size_by_name[cname] = len(open(cpath).read().split())
        sorted_chars = list(reversed(sorted(list(size_by_name.items()), key=operator.itemgetter(1))))
        for pair in sorted_chars[0:number]:
            print(pair)
        return sorted_chars


p = transcript_parser()
p.parseTranscript('madmen')
