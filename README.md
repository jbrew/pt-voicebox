# pt-voicebox
this is a writing engine intended to imitate the predictive text function on smartphones

The classes are structured as follows:

- a corpus has a tree with the frequencies of all n-grams up to a certain size present in a source, and information about which words precede and follow these

- a voice is a weighted combination of corpora

- a voicebox contains a list of voices, and has a user writing loop that allows for switching between them on the fly


Instructions:

SETTING UP THE FOLDER
1. Download the folder (using the green button in the top right of the repo) and save it on your desktop as pt-voicebox
2. Create a text file for each source text you want to use. Save them inside the 'texts' folder within voicebox (pt-voicebox/texts)
 
RUNNING THE PROGRAM
1. Open the Mac application called Terminal
2. Enter this into the Terminal window: cd Desktop/pt-voicebox
         (This means “change directory to voicebox”)
3. Enter this into the Terminal window: python voicebox.py
         (This means “use python to run the script called voicebox.py”)
4. Follow the onscreen instructions.
