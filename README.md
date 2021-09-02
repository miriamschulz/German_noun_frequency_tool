# German noun frequency search tool

## About

This folder contains the program 'target_search_interactive.py' which retrieves German nouns similar in frequency, length and morphological criteria to some input noun.

Search criteria can be interactively adjusted while executing the program.

The program was designed to help in the construction of psycholinguistic stimuli that require several target words of comparable frequency, length, gender, etc.

USAGE:
`python target_search_interactive.py `

## Requirements

To run the code, check that the file `deWaC_freqlist.tsv` is in the same directory as the code file.

For the morphological analysis, [download DEMorphy for python](https://github.com/DuyguA/DEMorphy).
Additionally, [download the `words.dg` file](https://github.com/DuyguA/DEMorphy/blob/master/demorphy/data/words.dg) and store it in DEMorphy's data folder, e.g. under:
`anaconda3/lib/python3.6/site-packages/demorphy-1.0-py3.6.egg/demorphy/data/`.

## References

Altinok, D.: DEMorphy, German Language Analyzer. Berlin, 2018.

M. Baroni, S. Bernardini, A. Ferraresi and E. Zanchetta. 2009. The WaCky Wide Web: A Collection of Very Large Linguistically Processed Web-Crawled Corpora. Language Resources and Evaluation 43 (3): 209-226.
