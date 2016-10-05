# pt-voicebox
This is a writing interface intended to imitate the predictive text function on smartphones. It is not a bot! You have to use it.

The classes are structured as follows:

- a corpus has a tree with the frequencies of all n-grams up to a certain size present in a source, and information about which words precede and follow these

- a voice is a weighted combination of corpora

- a voicebox contains a list of voices, and has a user writing loop that allows for switching between them on the fly

# overview of algorithm

The approach to generating word lists is Markov-esque but is not strictly a Markov process, which would need to be stochastic. Here, the user has the final decision.

At each step of the sentence, the script uses the n most recent words to determine a list of the m most likely words to come next. The Markov determination of this list is a weighted combination of several lists, with higher weights given to lists of words that followed larger n-grams that constitute the immediate context.

For instance, when n=2 and the most recent two words in the sentence are "my big", the following lists factor into supplying the list of m words:

- list of words following "my big" (this is given the highest weight)
- list of words following "big" (next highest weight)
- list of words occurring two after "my" (lower weight)
- list of words occurring most frequently overall in the source (this list never changes and is a fallback when, as often happens with shorter sources, the other three lists are bare)

A similar pattern holds for higher values of n, with larger n-grams emphasized ver smaller n-grams, and closer n-grams emphasized over more distant ones.

# quick and dirty instructions for use

SETTING UP THE FOLDER
- 1. Download the folder (using the green button in the top right of the repo) and save it on your desktop as pt-voicebox
- 2. Create a text file for each source text you want to use. Save them inside the 'texts' folder within voicebox (pt-voicebox/texts)
 
RUNNING THE PROGRAM
- 1. Open the Mac application called Terminal
- 2. Enter this into the Terminal window: cd Desktop/pt-voicebox
         (This means “change directory to voicebox”)
- 3. Enter this into the Terminal window: python voicebox.py
         (This means “use python to run the script called voicebox.py”)
- 4. Follow the onscreen instructions.
