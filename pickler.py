__author__ = 'jamiebrew'

import cPickle as pickle

# saves an object to a file
def save_object(obj, path):
    with open(path, 'wb') as output:
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)

def loadobject(path):
    with open(path, 'rb') as input:
        obj = pickle.load(input)
    return obj