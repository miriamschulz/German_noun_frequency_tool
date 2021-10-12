'''
12 October 2021
Miriam Schulz
mschulz@coli.uni-saarland.de

This script checks for the existence of a verb in the bigram file
(if the verb does not exist at all, it is probable that SpaCy gave it an
incorrect POS-tag; to fix this, run bigram_extractor_manual.py for this verb)

USAGE: bigram_check_verb_existence.py <yourverb>
'''

import sys

def verb_exists(bigramfile, testverb):
    with open(bigramfile, 'r', encoding='utf-8') as F:
        i = 0
        n_bigrams = 3306296  # number of lines in original bigram file
        for line in F:
            line = line.split('\t')
            i += 1
            if i % 100 == 0:
                print(' Verb search progress: {:2.0%}'\
                      .format(i/n_bigrams), end='\r')
            verb = line[3]
            if verb == testverb:
                return True
    return False

if __name__ == '__main__':

    try:
        verb = sys.argv[1].strip()
    except:
        print('USAGE: python bigram_extractor_manual.py <yourverb>\n')
        sys.exit()
    print('Searching for bigrams with the verb: {}'.format(verb))

    red_col = '\u001b[31;1m'    # bright red
    green_col = '\u001b[32;1m'  # bright green
    reset_col = '\u001b[0m'     # reset to normal

    bigramfile = 'bigrams_noun_verb_freq2+.tsv'
    existence = verb_exists(bigramfile, verb)
    if existence == True:
        print('{}The verb \'{}\' was found in the bigram file.\n{}'\
              .format(green_col, verb, reset_col))
    else:
        print('{}Could not find the verb \'{}\' in the bigram file.{}\n'\
              .format(red_col, verb, reset_col))
