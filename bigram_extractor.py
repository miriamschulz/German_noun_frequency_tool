'''
7 September 2021
Miriam Schulz
mschulz@coli.uni-saarland.de

This script extracts all bigrams of the form NOUN-VERB (or NOUN-AUX)
from the deWaC lemma bigram list, to be further used for stimuli creation.

To increase speed, the script first checks if the second lemma ends with -n;
if yes, its POS tag is extracted using spaCy.
Then, the POS tag of the first lemma is calculated, and if it is a NOUN,
the bigram is added to the final list of NOUN-VERB bigrams.

This version uses a cutoff value to exclude very rare bigrams of total count 1.

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

def get_verb_bigrams(filename, cutoff_value, verb):
    '''
    Extracts bigrams from the deWaC corpus lemmatized bigram list.
    Keeps only bigrams that end with a verb and start with a noun.
    If a cutoff_value larger than 0 is given as input, bigrams whose count
    in the corpus is equal to or lower than this cutoff value will be skipped.
    '''
    print('Starting bigram extraction...')
    print('(Extracting bigrams with a frequency of more than {})'\
          .format(cutoff_value))
    nlp = spacy.load("de_core_news_sm", disable=["tok2vec", "parser", \
                     "attribute_ruler", "lemmatizer", "ner"])
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
        if cutoff_value in cutoff_n.keys():
            n = cutoff_n[cutoff_value]
        for line in F:
            i += 1
            if i % 1000 == 0:
                print(' Progress: {:2.2%} (processed {} bigrams)'\
                      .format(i/n, i), end='\r')
            line = line.split()
            if len(line) >= 3:  # to avoid errors in case of incomplete lines
                bigram_count = line[0]
                lemma1 = line[1]
                lemma2 = line[2]
                if bigram_count == cutoff_value:
                    break
                # Alternatively, only process bigrams with this count:
                # if not bigram_count == cutoff_value:
                #     continue
                if verb == None:
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
                else:
                    if lemma2 == verb:
                        lemma2_pos = 'VERB'
                        lemma1_analysis = nlp(lemma1)[0]
                        lemma1_pos = lemma1_analysis.pos_
                        if lemma1_pos == 'NOUN':
                            keep_bigrams.append((bigram_count,
                                                 lemma1, lemma1_pos,
                                                 lemma2, lemma2_pos))
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

    # Extract bigrams up to (but excluding) a certain minimum frequency count
    cutoff_value = '1'  # '1' will process bigrams with a count > 1
    verb = None  # verbs can be entered in the extension file to this script
    bigrams = get_verb_bigrams('de.lemma.bigrams.utf8.txt', cutoff_value, verb)

    # Write extracted bigrams to file
    outfilename = 'bigrams_noun_verb.tsv'
    write_bigrams_to_file(bigrams, outfilename)
