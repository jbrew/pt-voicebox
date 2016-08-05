# pt-voicebox
this is a writing engine intended to imitate the predictive text function on smartphones

The classes are structured as follows:

- a corpus has a tree with the frequencies of all n-grams up to a certain size present in a source, and information about which words precede and follow these

- a voice is a weighted combination of corpora

- a voicebox contains a list of voices, and has a user writing loop that allows for switching between them on the fly
