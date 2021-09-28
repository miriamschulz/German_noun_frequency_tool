'''
1 September 2021
Miriam Schulz
mschulz@coli.uni-saarland.de

Tool for stimuli creation
Version 5 – interactive version for the German deWaC noun frequency list

This script extracts singular nouns and their frequencies from the deWaC
word frequency list downloaded from:
https://wacky.sslmit.unibo.it/doku.php?id=frequency_lists

Nouns are morphologically analyzed using DEMorphy.
Download DEMorphy from: https://github.com/DuyguA/DEMorphy
To install, additionally download the words.dg file and store it
in DEMorphy's data folder, e.g. under:
anaconda3/lib/python3.6/site-packages/demorphy-1.0-py3.6.egg/demorphy/data/

USAGE: python German_noun_frequency_tool.py

MODE 1: similar target search (Search-by-Noun)
Input: a target word
Searches for nouns that are similar to the input target word in frequency,
length and morphological criteria (gender, case and numerus)

MODE 2: frequency search (Search-by-Frequency)
Input: a frequency (number)
Extracts all nouns with a similar frequency

Search parameters (interactively adjustable, except for word frequency):
- Word frequency:
  Depending on the frequency of the input target word (MODE 1) or the
  input frequency (MODE 2), words with compatible frequencies are returned.
  3 frequency classes are distinguished:
  * group 1: input_frequency >= 100: returns nouns with frequencies >= 100
  * group 2: 10 <= input_frequency < 100: returns nouns with a
    frequency difference of +- 5
  * group 3: input_frequency < 10: nouns with frequency difference of +- 1
- Word length: Restricts the search to nouns similar in length to the input
  target (in MODE 1). Default value for the length difference: 2
- Morphological criteria: analysis of gender, case, numerus (using DEMorphy)
- Results are sorted by increasing frequency difference from the input target
- An additional refinement of the search results allows the user to
  restrict the results to those nouns that can occur together with a specific
  verb (with occurrence here meaning that the count of the bigram NOUN + VERB
  (lemmatized) is >= 2)

'''

import sys
import os
from demorphy import Analyzer


def start_search():

    '''
    Starts the search by obtaining user input (a word or a frequency)
    and setting the search defaults
    '''

    os.system('cls' if os.name == 'nt' else 'clear')  # clear terminal

    print('\t' + '-' * 26)
    print('\t{}GERMAN NOUN FREQUENCY TOOL{}'.format(heading_col, reset_col))
    print('\t' + '-' * 26, '\n')

    print('{}Please enter either a target word (e.g. Haus) \n'
          'or a search frequency (int or float, e.g. 5.5):{}'\
          .format(input_col, reset_col), end=' ')
    user_input = check_input(input().strip())

    # Differentiate between frequency and word input:
    try:
        search_freq = float(user_input)
        # Set search defaults
        genders = ['masc', 'fem', 'neut']
        length_min = 1
        length_max = 100
    except ValueError:
        target_word = user_input
        target_freq = get_target_freq(target_word)
        t_genders, t_cases, t_nums = get_target_morph(target_word)
        print('\n\tChosen target: \t\t\'{}\''.format(target_word))
        print('\tFrequency rank: \t{} per million'.format(target_freq))
        print('\tWord length: \t\t{} characters'.format(len(target_word)))
        print('\tPossible genders: \t{}'.format(', '.join(t_genders)))
        print('\tPossible cases: \t{}'.format(', '.join(t_cases)))
        print('\tPossible numerus: \t{}'.format(', '.join(t_nums)))

        length_diff = 2
        length_min = len(target_word) - length_diff
        if length_min <= 0:
            length_min = 1
        length_max = len(target_word) + length_diff
        genders = t_genders
        search_freq = target_freq

    # Shared search defaults
    cases = ['dat', 'acc']
    numerus = ['sing']

    # Customize search
    genders, cases, numerus, length_min, length_max = \
        search_customization(genders, cases, numerus, length_min, length_max)

    # Search for similar targets
    freq_list = main_search(search_freq, length_min, length_max,
                            genders, cases, numerus)

    continue_options(freq_list)

def main_search(search_freq, length_min, length_max, genders, cases, numerus):

    '''
    Reads the file containing the word frequencies and extracts + prints words
    on the basis of the specified search criteria
    '''

    print('''\nSearching for nouns...

        Search criteria
        * Search frequency: \t{} per million
        * Word length: \t\t{} to {} characters
        * Genders: \t\t{}
        * Cases: \t\t{}
        * Numerus: \t\t{}
        '''.format(search_freq, length_min, length_max,
                   '/'.join(genders), '/'.join(cases), '/'.join(numerus)))

    freq_dict = dict()
    with open('deWaC_freqlist.tsv', 'r', encoding='utf-8') as F:
        i = 0
        n = 1974122  # total lines in deWaC_freqlist.tsv
        for line in F:
            line=line.split()
            word=line[0]
            freq=float(line[1])
            gender=line[3]
            case=line[4]
            num=line[5]
            # Check frequency
            freq_eval = frequency_check(search_freq, freq)
            if freq_eval == True:
                # Check length
                if length_min <= len(word) <= length_max:
                    # Check morphological criteria
                    if (gender in genders) and \
                       (num in numerus) and \
                       (case in cases):
                        if word in freq_dict.keys():
                            if freq in freq_dict[word].keys():
                                freq_dict = add_to_dict(freq_dict, word, freq,
                                                        gender, case, num)
                            else:
                                freq_dict[word][freq] = dict()
                                freq_dict[word][freq]['gender'] =  set()
                                freq_dict[word][freq]['case'] = set()
                                freq_dict[word][freq]['numerus'] = set()
                                freq_dict = add_to_dict(freq_dict, word, freq,
                                                        gender, case, num)
                        else:
                            freq_dict[word] = dict()
                            freq_dict[word][freq] = dict()
                            freq_dict[word][freq]['gender'] =  set()
                            freq_dict[word][freq]['case'] = set()
                            freq_dict[word][freq]['numerus'] = set()
                            freq_dict = add_to_dict(freq_dict, word, freq,
                                                    gender, case, num)
            i += 1
            if i % 1000 == 0:
                print(' Noun search progress: {:2.0%}'.format(i/n), end='\r')

    # Transform the frequency dictionary to a list
    freq_list = []
    for word, f in freq_dict.items():
        for freq, morph_info in f.items():
            morph_all = []
            for k, m in morph_info.items():
                m = '/'.join(list(m))
                morph_all.append(m)
            freq_list.append((word, freq, morph_all[0],
                              morph_all[1], morph_all[2]))

    # Reorder list by increasing difference from the target freq:
    freq_list = sorted(freq_list, key=lambda x: abs(search_freq - x[1]))

    # Print search results
    print('\n\nFound the following {} nouns with similar frequency:\n'\
          .format(len(freq_list)))
    formatting_pattern = '{0: <25}|{1: ^13}|{2: ^20}|{3: ^20}|{4: ^12}'
    print('\t' + formatting_pattern.format('           NOUN', 'FREQUENCY',
                                           'GENDERS', 'CASES', 'NUMERUS'))
    print('\t' + '_'*94)
    j = 0
    for entry in freq_list:
        line = formatting_pattern.format(*entry)
        if j % 2 == 0:
            print('\t{}{}{}'.format(back_search, line, reset_col))
        else:
            print('\t'+line)
        j += 1

    return freq_list

def search_customization(genders, cases, numerus,
                        length_min, length_max):

    '''
    Promts the user to enter their own search criteria
    (e.g. search only for plural nouns)
    '''

    possible_cases = ['nom', 'gen', 'dat', 'acc']
    possible_numbers = ['sing', 'plu']
    possible_genders = ['fem', 'masc', 'neut']

    # Search customization
    print('\nCustomize the search by changing the default ')
    print('search gender(s) / case(s) / numerus / word length difference?')
    print('{}Press \'y\' for yes, otherwise press Enter.{}'\
          .format(input_col, reset_col), end=' ')
    choice_custom = check_input(input().strip().lower())
    if choice_custom != 'y':
        return genders, cases, numerus, length_min, length_max

    print('\n{}Type the desired word length range, gender(s), case(s) '
          'and/or numerus.'
          '\nSeparate each by a comma.{}'\
          .format(input_col, reset_col))
    print('\tOptions:')
    print('\t*  LENGTH RANGE:\te.g. \'8-10\' for words of '
          '8 to 10 characters in length')
    print('\t*  CASE:\t\tnom, gen, dat, acc')
    print('\t*  GENDER:\t\tmasc, fem, neut')
    print('\t*  NUMERUS:\t\tsing OR plu')
    print('\t*  Remove all search filters: simply type \'all\'')
    print('(not all entries are required, e.g. it is possible to enter only '
          '\'3-5, nom, gen\' \nto restrict the search to nominative and '
          'genitive nouns with a word length \nof 3 to 5 characters.)')

    custom_input = check_input(input().lower())
    customizations = [el.strip() for el in custom_input.split(',')]

    if 'all' in customizations:
        return possible_genders, possible_cases, possible_numbers, 1, 100

    new_cases = []
    new_genders = []
    new_numbers = []
    for entry in customizations:
        if '-' in entry:
            length_min, length_max = entry.split('-')
            try:
                length_min = int(length_min)
                length_max = int(length_max)
            except:
                pass
        elif entry in possible_cases:
            new_cases.append(entry)
        elif entry in possible_numbers:
            new_numbers.append(entry)
        elif entry in possible_genders:
            new_genders.append(entry)
    if new_cases != []:
        cases = new_cases
    if new_genders != []:
        genders = new_genders
    if new_numbers != []:
        numerus = new_numbers

    return genders, cases, numerus, length_min, length_max

def frequency_check(target_freq, freq):
    '''
    Evaluates a noun's frequency against the frequency of the target word.
    Returns True if both input frequencies are in the same of 3 frequency
    groups, and therein, within a maximally allowed distance:
    * larger than 100 per million: any distance
    * 10 to 100 per million: +- 5
    * fewer than 10 per million: +- 1
    '''
    if (target_freq < 10):
        if target_freq-1 <= freq <= target_freq+1:
            return True
    elif (target_freq >= 100) and (freq >= 100):
        return True
    else:  # i.e., if 10 <= search_freq < 100
        if (target_freq-5 <= freq <= target_freq+5):
            if (freq > 10):
                return True
            elif (target_freq-1 <= freq <= target_freq+1):
                return True
    return False

def add_to_dict(freq_dict, word, freq, gender, case, num):
    freq_dict[word][freq]['gender'].add(gender)
    freq_dict[word][freq]['case'].add(case)
    freq_dict[word][freq]['numerus'].add(num)
    return freq_dict

def get_target_freq(target_word):
    '''
    Extracts the frequency of the input target word from the frequency file
    '''
    with open('deWaC_freqlist.tsv', 'r', encoding='utf-8') as F:
        for line in F:
            line=line.split()
            word=line[0]
            freq=float(line[1])
            if word == target_word:
                return freq
        # If no target word is found, try again:
        print('\n{}Target word not found. '
              'Press Enter to try again with another target or frequency.{}'\
              .format(warn_col, reset_col))
        choice = check_input(input().strip())
        start_search()

def get_target_morph(noun):
    '''
    Extracts the possible genders, cases and numbers of the input target word
    '''
    s = analyzer.analyze(noun)
    genders = []
    cases = []
    numbers = []
    for x in s:
        genders.append(x.gender)
        cases.append(x.case)
        numbers.append(x.numerus)
    return set(genders), set(cases), set(numbers)

def bigram_search(freq_list):
    '''
    Checks whether the nouns found in the main search occur with an
    input verb in the lemmatized deWaC bigram list
    '''
    print('\n{}Please enter a verb (infinitive) to check for '
          'co-occurrence with the retrieved nouns:{}'\
          .format(input_col, reset_col), end=' ')
    # Transform freq_list to dict for easy lookup:
    freq_dict = {}
    for (noun, freq, genders, cases, nums) in freq_list:
        freq_dict[noun] = (freq, genders, cases, nums)
    target_verb = check_input(input().strip())
    target_verb = target_verb.lower()
    keep_bigrams = []
    i = 0
    n_bigrams = 3306296  # number of lines in bigram file (previously 2405703)
    with open('bigrams_noun_verb_freq2+.tsv', 'r', encoding='utf-8') as F:
        for line in F:
            line = line.split('\t')
            i += 1
            if i % 100 == 0:
                print(' Verb search progress: {:2.0%}'.format(i/n_bigrams), end='\r')
            bigram_count = line[0]
            noun = line[1].title()  # .title() capitalizes the first letter
            noun_pos = line[2]
            verb = line[3]
            verb_pos = line[4]
            if verb == target_verb:
                if noun in freq_dict.keys():
                    freq = freq_dict[noun][0]
                    genders = freq_dict[noun][1]
                    cases = freq_dict[noun][2]
                    nums = freq_dict[noun][3]
                    keep_bigrams.append((bigram_count, noun, freq,
                                         genders, cases, nums))
    # Print search results
    if len(keep_bigrams) > 0:
        print('{}Out of the {} search results, {} nouns can occur with \'{}\':'\
              .format('\n'*2, len(freq_list), len(keep_bigrams), target_verb))
        print()
        formatting_pattern = '{0:^14}|{1:<25}|{2:^13}|{3:^20}|{4:^20}|{5:^12}'
        print('\t'+formatting_pattern.format('BIGRAM COUNT', '           NOUN',
                                             'FREQUENCY', 'GENDERS', 'CASES',
                                             'NUMERUS'))
        print('\t' + '_'*109)
        j = 0
        for entry in keep_bigrams:
            line=formatting_pattern.format(*entry)
            if j % 2 == 0:
                print('\t{}{}{}'.format(back_verbs, line, reset_col))
            else:
                print('\t'+line)
            j += 1
    else:
        print('\n{}Found no nouns in the search that can occur with \'{}\'{}.'\
              .format(warn_col, target_verb, reset_col))
    continue_options(freq_list)

def continue_options(freq_list):
    '''
    After completing a search, the user can choose between running a new search,
    doing a bigram search for the obtained nouns, or exiting the program.
    '''
    print('\nRun new search: press {}Enter{}'.format(input_col, reset_col))
    print('To check which of the nouns can follow a specific verb:'
          ' press {}\'v\'{}'.format(input_col, reset_col))
    print('To exit, type {}\'quit\' or \'q\'.{}'\
          .format(input_col, reset_col))
    continue_input = check_input(input().strip().lower())
    flag = True
    while True:
        if continue_input == '':
            flag = False
            start_search()
        elif continue_input == 'v':
            flag = False
            bigram_search(freq_list)
        else:
            print('{}Could not interpret choice. Please try again.{}'\
                  .format(warn_col, reset_col))
            continue_input = check_input(input().strip().lower())

def check_input(some_input):
    '''
    Function to be called on every user input that checks whether
    the user wishes to quit the program
    '''
    quit_signals = ['quit', 'exit', 'q', 'e']
    if some_input in quit_signals:
        print('\n{}Exiting...{}\n'.format(exit_col, reset_col))
        sys.exit()
    return some_input

if __name__ == '__main__':

    back_search = '\u001b[48;5;195m'  # light blue
    back_verbs = '\u001b[48;5;230m'   # light yellow
    heading_col = '\u001b[30;1m'  # bright black
    warn_col = '\u001b[31;1m'     # bright red
    input_col = '\u001b[36;1m'    # bright cyan
    sun_col = '\u001b[38;5;11m'   # bright pink
    exit_col = '\u001b[35;1m'     # bright dark blue
    reset_col = '\u001b[0m'

    # os.system('cls' if os.name == 'nt' else 'clear')  # clear terminal

    print('\n\n{}Welcome!{}'.format(heading_col, reset_col))
    print('{}  \\ /'.format(sun_col))
    print(' – o –')
    print('  / \\{}'.format(reset_col))

    print('\nThis program lets you search the deWaC German noun frequency list')
    print('(https://wacky.sslmit.unibo.it/doku.php?id=frequency_lists')
    print('to find German nouns by their frequency, length, and')
    print('morphological criteria (gender, case and numerus).')

    print('\nTo exit the program, simply type \'quit\' or \'q\' '
          'followed by Enter at any point.')
    print('\nPress any key to start.')
    start = check_input(input().strip())

    # Initialize gender classifier and POS tagger
    analyzer=Analyzer(char_subs_allowed=True)

    start_search()
