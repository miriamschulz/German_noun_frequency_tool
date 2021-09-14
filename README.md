# German noun frequency search tool

## About

This python program lets the user search through a list of German nouns sorted by frequency (constructed from the deWaC corpus (Baroni et al., 2009), downloaded from [here](https://wacky.sslmit.unibo.it/doku.php?id=frequency_lists); morphological annotation for case, gender and number through DEMorphy (Altinok, 2018)).

The program takes as input either a noun (such as 'Haus') or a frequency per million (such as '7') and retrieves nouns that are similar in frequency, divided into 3 frequency groups. Further search criteria include word length, gender, case and numerus. The search criteria can be interactively adjusted.

The program was designed to facilitate the construction of psycholinguistic stimuli that require several target words of comparable frequency, length, gender, etc.

## Mode 1: Search-by-Noun
In mode 1, the user enters a noun. By default, the program then searches for singular nouns in dative or accusative case with similar frequency that have the same gender as the input word and are at most two characters shorter or longer. These default settings can be changed manually at the start of every search.

## Mode 2: Search-by-Frequency
In mode 2, the input is a number (integer or float, e.g. '7.5') instead of a word. The program searches for all nouns that have a frequency per million similar to the input number. By default, the search is restricted to singular nouns in dative or accusative case like in mode 1. Unlike in mode 1, however, nouns of all genders and lengths are retrieved, unless the user specifies otherwise.

## The frequency criteria

Both search modes distinguish between three frequency groups, according to effects of word frequency observed in experiments:

* Group 1: all words with frequencies of >= 100 per million
* Group 2: words with a frequency between 10 and 100 per million: here frequencies should not differ by more than 5 per million
* Group 3: words with a frequency of less than 10 per million: here frequencies should not differ by more than 1 per million

Therefore, if an input word such as 'Haus' has a frequency of 140.86 per million, the search will retrieve nouns that also have a frequency of more than 100 per million.

A noun like 'Eichhörnchen', on the other hand, has a frequency of only 1.48 per million. The results will therefore be restricted to nouns with frequencies between 0.48 and 2.48 per million, equalling a search range of +-1 occurrences per one million tokens.

## Search extension: verb frames
After completing a search, an additional function allows to further refine the search results by checking which of the retrieved nouns can occur as the object of a specific verb. To this end, the user enters an infinitive verb and the program checks which of the nouns found in the search can precede this verb. This is done by iterating through a list of all bigrams of the form NOUN-VERB that was constructed from the deWaC lemmatized bigram list (full bigram list downloaded from [here](https://wacky.sslmit.unibo.it/doku.php?id=frequency_lists)).

The rationale behind using bigrams of the form NOUN-VERB is that in German's underlying SOV order, the object can directly precede the verb. Currently, only lemmatized bigrams that occur at least two times in the deWaC corpus are considered. Note that the results will also include NOUN-VERB pairs in which the noun is for instance the subject and not the object of the verb, since German has an SVO order in main clauses. To improve this search feature in the future, the NOUN-VERB bigram list could be replaced with a list of verb complements derived from the syntactically annotated version of the corpus, [SdeWaC](https://www.ims.uni-stuttgart.de/en/research/resources/corpora/sdewac/).

## Usage

`python german_noun_frequency_tool.py `

## Requirements

To run the code, check that the file `deWaC_freqlist.tsv` is downloaded to the same directory as the code file.

In order to run the verb frame extension, the file `bigrams_noun_verb_freq2+.tsv` should also be downloaded to the code directory.

For the morphological analysis, [download and install DEMorphy](https://github.com/DuyguA/DEMorphy).
Additionally, the [`words.dg`](https://github.com/DuyguA/DEMorphy/blob/master/demorphy/data/words.dg) file needs to be downloaded and stored in DEMorphy's data folder, e.g. under:
`anaconda3/lib/python3.6/site-packages/demorphy-1.0-py3.6.egg/demorphy/data/`.

## References

Altinok, D.: DEMorphy, German Language Analyzer. Berlin, 2018.

M. Baroni, S. Bernardini, A. Ferraresi and E. Zanchetta. 2009. The WaCky Wide Web: A Collection of Very Large Linguistically Processed Web-Crawled Corpora. Language Resources and Evaluation 43 (3): 209-226.
