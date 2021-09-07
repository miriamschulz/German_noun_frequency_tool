'''
7 September 2021
Miriam Schulz
mschulz@coli.uni-saarland.de

This script extracts all bigrams of the form NOUN-VERB (or NOUN-AUX)
from the deWaC lemma bigram list, to be further used for stimuli creation.

USAGE: python bigram_extractor.py

For POS tagging, install the German model for spaCy with:
python -m spacy download de_core_news_sm
More info at: https://explosion.ai/blog/german-model

SpaCy POS-tag set:

	 ADJ
	 ADP
	 ADV
	 AUX
	 CCONJ
	 DET
	 NOUN
	 NUM
	 PART
	 PRON
	 PROPN
	 PUNCT
	 SCONJ
	 VERB
	 X

'''

import spacy

def get_verb_bigrams(filename):
    print('Starting bigram extraction...')
    with open(filename, 'r', encoding='utf-8') as F:
        i = 0
        n = 100852376  # total number of lines in bigram lemma file
        keep_tags = ['AUX', 'VERB']
        keep_bigrams = []
        tags = set()
        for line in F:
            line = line.split()
            if len(line) >= 3:  # to avoid errors in case of empty lines
                bigram_count = line[0]
                lemma1 = line[1]
                lemma2 = line[2]
                lemma2_analysis = nlp(lemma2)[0]
                lemma2_pos = lemma2_analysis.pos_
                if lemma2_pos in keep_tags:
                    lemma1_analysis = nlp(lemma1)[0]
                    lemma1_pos = lemma1_analysis.pos_
                    if lemma1_pos == 'NOUN':
                        keep_bigrams.append((bigram_count, lemma1, lemma1_pos,
                                             lemma2, lemma2_pos))
                tags.add(lemma2_pos)

            i += 1
            # if i == 1000:
            #     break
            if i % 500 == 0:
                print(' Progress: {:2.2%} (processed {} bigrams)'\
                      .format(i/n, i), end='\r')

    print('\n\nProcessed all {} lines.'.format(i))
    print('\nFound {} NOUN-VERB bigrams.'.format(len(keep_bigrams)))
    print('\nFinal tag set ({} tags)'.format(len(tags)))
    for t in sorted(list(tags)):
        print('\t', t)

    return keep_bigrams

def write_bigrams_to_file(bigrams, outfilename):
    print('\nWriting noun-verb bigrams to file (filename: {})'.format(outfilename))
    output = open(outfilename, 'w', encoding='utf8')
    for line in bigrams:
        output.write('\t'.join(str(el) for el in line) + '\n')
    output.close()
    print('\nDone.\n')
    return

if __name__ == '__main__':
    nlp = spacy.load("de_core_news_sm", disable=["tok2vec", "parser", \
                     "attribute_ruler", "lemmatizer", "ner"])
    bigrams = get_verb_bigrams('de.lemma.bigrams.utf8.txt')
    outfilename = 'bigrams_noun_verb.tsv'
    write_bigrams_to_file(bigrams, outfilename)
