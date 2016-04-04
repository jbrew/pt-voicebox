# pt-voicebox
predictive text writing engine for multiple custom sources. designed to imitate the predictive text function on smartphones


# processing the source

The program eats a text file and stores information about it in a Python dictionary, each of whose entries represents a distinct word in the source along with its frequency and a subdictionary of all words that follow that word in the source, inside which are further nested subdictionaries of words that follow those words.

You could keep nesting dictionaries indefinitely, but this gets very computationally expensive. Since I was only interested in looking back two words, two levels of nesting was enough.

The top dictionary contains the program's entire knowledge of the source. An entry looks something like this...

 - Word: hello

 - Frequency: 11 (also represented as 11 / [total wordcount of source])

 - Subdictionary: {my, i, world, how}

This says that the word 'hello' has occurred 11 times in the source and has been followed variously by the words 'my', 'i' ,'world' and 'how'.

Note: The program downcaps everything and ignores mid-sentence punctuation.

The entry in the subdictionary for 'how' might look like this...

 - Word: how
   
 - Frequency: 2
   
 - Subdictionary: {are}

This says that the word 'how' has followed the 'word' hello twice, and that the phrase 'hello how' has only ever been followed by the word 'are'.

If we went even deeper, into the subdictionary entry for 'are', we would find this:

 - Word: are
   
 - Frequency: 2
   
 - Subdictionary: {}

From this entry, we know that the phrase 'hello how are' has occurred twice in the source. The subdictionary is empty not because nothing ever followed the phrase 'hello how are' but because when the overall dictionary was constructed, the program stopped nesting after two levels.

In this way, we can ask the top dictionary the following questions and expect answers every time:
   1. How often did word w1 occur?
   2. How often did word w2 follow w1?
   3. How often did word w3 follow the sequence (w1, w2)?

# predicting the next word

These questions turn out to be all we need.

Say we're trying to predict the next word of a sentence that's already at least two words long. We can get three pieces of information about the most recent words, m and n.
   A. The list of words that followed the sequence (m, n) most often
   B. The list of words that followed n most often
   C. The baseline list of most common words in the source

These three lists of words get different weights, and are combined to yield the list of words from which the user chooses (the equivalent of the three suggestions on the smartphone).

I weighted list A heavier than list B which in turn was heavier than list C. This means the program first emphasizes words that followed the whole sequence of (m, n), then words that follow (n), and finally words that are just very common in the overall source.

When the sentence is only one word long, list A is always empty, so the program uses a weighted combination of B and C.

When the sentence is empty, the program just gives you a list of the most common words in the source.

No matter the case, the program winds up with a list of all the unique words in the top dictionary (that is, all the words in the source), ranked according to the weighted score from all relevant lists.

The top n entries in this list are the user's n choices.

Having made a choice, the new word is added to the end of the sentence and the process repeats.

# two-back

There's a slight twist I haven't mentioned yet. In the top-level dictionary entries, I also include a second type of subdictionary that keeps track of the words that followed two spots after a given word.

So the full entry for the word 'hello' might look like this:

 - Word: hello

 - Frequency: 11 (also represented as 11 / [total wordcount of source])

 - Subdictionary 1: {my, i, world, how}

 - Subdictionary 2: {are, friend, am}

The last line tells us that 'are', 'friend' and 'am' have all occurred two spots after 'hello' but says nothing about the words between them. The entry for 'are', for example, could have a frequency of 4, from 2 instances of 'hello how are you' and 2 instances of 'hello world are you big'

This is a small point, but it sometimes proves useful. It does things like encourage the program to suggest the word "as" two places after another instance of the word "as", regardless of the word in between, which reflects a useful pattern about how "as" appears in most English sources.

# is it markov chains?

One of the most frequent questions I've gotten about this program is whether it is essentially Markov chains.

So, here's my understanding of what a Markov chain is: *a process in which each state has a fixed set of probabilities determining which state it moves to next.*

According to this definition, my program is not implementing a Markov chain, because of the capricious human who gets final say. The generation of options is automatic and Markov-esque, but the final choice is human.

That said, you could easily modify this program to be a bona fide Markov bot. Instead of showing the user a list of the n continuations with the highest likelihood scores, the algorithm chooses one based on these scores. You could have it choose randomly among that n highest scores, or proportionally to the scores. This, I think, would make the program essentially equivalent many markov generative bots I've seen. It would also change the output significantly.
