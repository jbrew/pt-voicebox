# pt-voicebox
This is a writing interface intended to imitate the predictive text function on smartphones. It is not a bot! A user has to be involved.

# Getting Started (Mac OS X)
#### Running the Program
1. Open the Mac application called Terminal
2. Enter `cd ~/Desktop` or wherever you would like to download the project (`cd` means "Change Directory" and `~/Desktop` is a shortcut to your desktop) 
3. Enter `git clone https://github.com/jbrew/pt-voicebox.git` to download the project
4. Enter `cd pt-voicebox` to go into the project directory
5. Enter `pip install -r requirements.txt` to download the project dependencies
6. Enter `bin/voicebox` and follow the onscreen instructions

#### Adding Your Own Source Texts
1. Enter `cd ~/Desktop/pt-voicebox` or wherever you downloaded the project
2. Create a text file for each source text you want to use. Save them inside the `texts` folder within voicebox (`pt-voicebox/texts`)

#### Running the Tests
1. Enter `cd ~/Desktop/pt-voicebox` or wherever you downloaded the project
2. Enter `nosetests tests`

# Project Structure
The classes are structured as follows:

- A corpus has a tree with the frequencies of all n-grams up to a certain size present in a source, and information about which words precede and follow these
- A voice is a weighted combination of corpora
- A voicebox contains a list of voices, and has a user writing loop that allows for switching between them on the fly

# Algorithm Overview
The approach to generating word lists is Markov-esque but is not strictly a Markov process, which would need to be stochastic. Here, the user has the final decision.

At each step of the sentence, the script uses the n most recent words to determine a list of the m most likely words to come next. The Markov determination of this list is a weighted combination of several lists, with higher weights given to lists of words that followed larger n-grams that constitute the immediate context.

For instance, when n=2 and the most recent two words in the sentence are "my big", the following lists factor into supplying the list of m words:

- List of words following "my big" (this is given the highest weight)
- List of words following "big" (next highest weight)
- List of words occurring two after "my" (lower weight)
- List of words occurring most frequently overall in the source (this list never changes and is a fallback when, as often happens with shorter sources, the other three lists are bare)

A similar pattern holds for higher values of n, with larger n-grams emphasized ver smaller n-grams, and closer n-grams emphasized over more distant ones.
