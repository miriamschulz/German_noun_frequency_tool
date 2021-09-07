# German noun frequency search tool

## About

This is a python program that lets the user search through a list of German nouns sorted by frequency (constructed from the deWaC corpus (Baroni et al., 2009), downloaded from [here](https://wacky.sslmit.unibo.it/doku.php?id=frequency_lists); morphological annotation through DEMorphy (Altinok, 2018)).

The program takes as input either a noun or a frequency and retrieves German nouns that are similar in frequency, divided into 3 frequency groups. Additional search criteria include word length, gender, case and numerus.

The program was designed to facilitate the construction of psycholinguistic stimuli that require several target words of comparable frequency, length, gender, etc.

## Usage

`python german_noun_frequency_tool.py `

## Requirements

To run the code, check that the file `deWaC_freqlist.tsv` is downloaded to the same directory as the code file.

For the morphological analysis, [download and install DEMorphy](https://github.com/DuyguA/DEMorphy).
Additionally, [download the `words.dg` file](https://github.com/DuyguA/DEMorphy/blob/master/demorphy/data/words.dg) and store it in DEMorphy's data folder, e.g. under:
`anaconda3/lib/python3.6/site-packages/demorphy-1.0-py3.6.egg/demorphy/data/`.

## References

Altinok, D.: DEMorphy, German Language Analyzer. Berlin, 2018.

M. Baroni, S. Bernardini, A. Ferraresi and E. Zanchetta. 2009. The WaCky Wide Web: A Collection of Very Large Linguistically Processed Web-Crawled Corpora. Language Resources and Evaluation 43 (3): 209-226.
