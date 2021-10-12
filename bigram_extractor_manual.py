'''
12 October 2021
Miriam Schulz
mschulz@coli.uni-saarland.de

Extension of the bigram extractor that manually extracts the noun-verb bigrams
for a particular input verb (to correct for verbs that SpaCy's POS-tagger
misclassified as nouns).

In step 1, the script checks whether the verb is already present in the
noun-verb bigram file.

If the verb is not found, the user can choose in step 2 whether or not to
append bigrams for this verb to the noun-verb bigram file.

USAGE: python bigram_extractor_manual.py <yourverb>

'''

import sys
from bigram_extractor import get_verb_bigrams


import sys

def verb_exists(bigramfile, verb):
    '''
    Checks whether the verb is already present in the bigram file
    '''
    print('Searching for bigrams with the verb: {}'.format(verb))
    with open(bigramfile, 'r', encoding='utf-8') as F:
        i = 0
        n_bigrams = 3306296  # number of lines in original bigram file
        for line in F:
            line = line.split('\t')
            i += 1
            if i % 100 == 0:
                print(' Verb search progress: {:2.0%}'\
                      .format(i/n_bigrams), end='\r')
            currentverb = line[3]
            if currentverb == verb:
                return True
    return False

def add_bigrams_to_file(verb, bigramfile):
    cutoff = '1'  # '0' will process all bigrams
    print('The default cutoff value for the bigram frequency is {}.'\
          .format(cutoff))
    print('To continue with this value, press Enter, otherwise enter a '\
          'new cutoff value.')
    cutoff_choice = input().strip()
    if cutoff_choice != '':
        cutoff = cutoff_choice
    print('Getting bigrams for the verb: {} with cutoff value {}.'\
          .format(verb, cutoff))

    # Extract bigrams up to (but excluding) a certain min frequency count
    bigrams = get_verb_bigrams('de.lemma.bigrams.utf8.txt', cutoff, verb)

    # Append the new bigrams to the bigrams file
    file_appender(bigramfile, bigrams)

    return

def file_appender(filename, newlines):
    '''
    Appends lines to the end of a file
    '''
    print('Adding the new bigrams to the bigram file...')
    with open(filename, 'a') as f:
        for line in newlines:
            f.write('\t'.join(str(el) for el in line) + '\n')
    print('Bigrams added.\n')
    return

if __name__ == '__main__':

    # Check presence of command line argument
    try:
        verb = sys.argv[1].strip()
    except:
        print('\nUSAGE: python bigram_extractor_manual.py <yourverb>\n')
        sys.exit()

    # Terminal colors
    red_col = '\u001b[31;1m'    # bright red
    green_col = '\u001b[32;1m'  # bright green
    reset_col = '\u001b[0m'     # reset to normal

    # STEP 1: search for the verb in the noun-verb bigram file
    bigramfile = 'bigrams_noun_verb_freq2+.tsv'
    existence = verb_exists(bigramfile, verb)
    if existence == True:
        print('{}The verb \'{}\' was found in the bigram file.\n{}'\
              .format(green_col, verb, reset_col))
        sys.exit()
    else:
        print('{}Could not find the verb \'{}\' in the bigram file.{}\n'\
                  .format(red_col, verb, reset_col))

    # STEP 2 (optional): add bigrams with the verb to the bigram file
    print('Add bigrams containing \'{}\' to the noun-verb bigrams file ({})?'\
          .format(verb, bigramfile))
    print('(y/n)')
    choice = input().strip()
    if choice.lower() == 'y':
        add_bigrams_to_file(verb, bigramfile)
    else:
        print('Not adding bigrams.\n')
