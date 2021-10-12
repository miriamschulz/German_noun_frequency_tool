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
extract and add (prepend) bigrams for this verb to the noun-verb bigram file.

USAGE: python bigram_extractor_manual.py <yourverb>

'''

import sys
from bigram_extractor import get_verb_bigrams


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


def file_prepender(filename, newlines):
    '''
    Prepends lines to the beginning of a file
    '''
    with open(filename, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        for line in newlines:
            f.write('\t'.join(str(el) for el in line) + '\n')
        f.write(content)

if __name__ == '__main__':

    try:
        verb = sys.argv[1].strip()
    except:
        print('\nUSAGE: python bigram_extractor_manual.py <yourverb>\n')
        sys.exit()

    # STEP 1: search for the verb in the noun-verb bigram file
    print('Searching for bigrams with the verb: {}'.format(verb))

    red_col = '\u001b[31;1m'    # bright red
    green_col = '\u001b[32;1m'  # bright green
    reset_col = '\u001b[0m'     # reset to normal

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

        # Prepend the new bigrams to the bigrams file
        print('Adding the new bigrams to the bigram file...')
        bigramfile_noun_verb = 'bigrams_noun_verb_freq2+.tsv'
        file_prepender(bigramfile_noun_verb, bigrams)
        print('Bigrams added.\n')

    else:
        print('Not adding bigrams.\n')
