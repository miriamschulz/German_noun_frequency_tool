'''

## Version that filters for inf. verbs by checking if a words ends with -n
and only then uses spacy for POS-detection;
uses a cutoff point for bigram minimal count ##

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

def get_verb_bigrams(filename, cutoff_count):
    '''
    Extracts bigrams from the deWaC corpus lemmatized bigram list.
    Keeps only bigrams that end with a verb and start with a noun.
    If a cutoff_count larger than 0 is given as input, bigrams whose count
    in the corpus is equal to or lower than this cutoff value will be skipped.
    '''
    print('Starting bigram extraction...')
    with open(filename, 'r', encoding='utf-8') as F:
        i = 0
        keep_tags = ['AUX', 'VERB']
        keep_bigrams = []
        cutoff_n = {'1': 35833352,
                    '2': 21349329,
                    '3': 15635096,
                    '4': 12425589,
                    '5': 10417585,
                    '10': 5964572}
        n = 100852376  # total number of lines in bigram lemma file
        if cutoff_count in cutoff_n.keys():
            n = cutoff_n[cutoff_count]
        for line in F:
            line = line.split()
            if len(line) >= 3:  # to avoid errors in case of empty lines
                bigram_count = line[0]
                lemma1 = line[1]
                lemma2 = line[2]
                if bigram_count == cutoff_count:
                    break
                if lemma2[-1] == 'n':  # superficial check for verb
                    lemma2_analysis = nlp(lemma2)[0]
                    lemma2_pos = lemma2_analysis.pos_
                    if lemma2_pos in keep_tags:
                        lemma1_analysis = nlp(lemma1)[0]
                        lemma1_pos = lemma1_analysis.pos_
                        if lemma1_pos == 'NOUN':
                            keep_bigrams.append((bigram_count,
                                                 lemma1, lemma1_pos,
                                                 lemma2, lemma2_pos))

            i += 1
            if i % 1000 == 0:
                print(' Progress: {:2.2%} (processed {} bigrams)'\
                      .format(i/n, i), end='\r')
            # if i == 10000:
            #     break

    print('\n\nProcessed all {} lines.'.format(i))
    print('\nFound {} NOUN-VERB bigrams.'.format(len(keep_bigrams)))
    return keep_bigrams

def write_bigrams_to_file(bigrams, outfilename):
    '''
    Writes the extracted noun-verb bigrams to an output file.
    '''
    print('\nWriting noun-verb bigrams to file (filename: {})'\
          .format(outfilename))
    output = open(outfilename, 'w', encoding='utf8')
    for line in bigrams:
        output.write('\t'.join(str(el) for el in line) + '\n')
    output.close()
    print('\nDone.\n')
    return

if __name__ == '__main__':

    nlp = spacy.load("de_core_news_sm", disable=["tok2vec", "parser", \
                     "attribute_ruler", "lemmatizer", "ner"])

    # Extract bigrams up to a certain minimum frequency count
    cutoff_count = '5'
    bigrams = get_verb_bigrams('de.lemma.bigrams.utf8.txt', cutoff_count)

    # Write extracted bigrams to file
    outfilename = 'bigrams_noun_verb.tsv'
    write_bigrams_to_file(bigrams, outfilename)
