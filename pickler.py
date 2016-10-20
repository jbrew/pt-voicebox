from __future__ import absolute_import
__author__ = 'jamiebrew'

import six.moves.cPickle as pickle


def save_object(obj, path):
    """saves an object to a file"""
    with open(path, 'wb') as output:
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)


def loadobject(path):
    with open(path, 'rb') as input:
        obj = pickle.load(input)
    return obj
