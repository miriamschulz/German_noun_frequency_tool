'''
1 September 2021
Miriam Schulz

Tool for stimuli creation
Version 4 – interactive version for the German deWaC noun frequency list

This script extracts singular nouns and their frequencies from the deWaC
word frequency list downloaded from:
https://wacky.sslmit.unibo.it/doku.php?id=frequency_lists

Nouns are morphologically analyzed using DEMorphy.
Download DEMorphy from: https://github.com/DuyguA/DEMorphy
To install, additionally download the words.dg file and store it
in DEMorphy's data folder, e.g. under:
anaconda3/lib/python3.6/site-packages/demorphy-1.0-py3.6.egg/demorphy/data/

USAGE: python German_noun_frequency_tool.py

MODE 1: similar target search
Input: a target word
Searches for nouns that are similar to the input target word in frequency,
length and morphological criteria (gender, case and numerus)

MODE 2: frequency search
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

'''

import sys
import os
from demorphy import Analyzer


def search_by_target():

    '''
    MODE 1: use an input noun to search for similar nouns
    '''

    os.system('cls' if os.name == 'nt' else 'clear')  # clear terminal

    print('Currently in MODE 1: Search-by-Target'.upper())
    print('\nTo exit the program, type \'quit\' at any time.')
    print('\nPlease enter a target word:')
    target_word = check_quit(input().strip())
    target_freq = get_target_freq(target_word)
    t_genders, t_cases, t_nums = get_target_morph(target_word)
    print('\n\tChosen target: \'{}\''.format(target_word))
    print('\tFrequency rank: {} per million'.format(target_freq))
    print('\tPossible genders: {}'.format(', '.join(t_genders)))

    # Define search defaults
    length_diff = 2
    cases = ['dat', 'acc']
    numerus = ['sing']

    # Customize search
    genders, cases, numerus, length_diff = search_customization(t_genders,
                                                                cases,
                                                                numerus,
                                                                length_diff)

    length_min = max(1, len(target_word) - length_diff)
    length_max = len(target_word) + length_diff

    # Search for similar targets
    main_search(target_freq, length_min, length_max, genders, cases, numerus)

    print('\nRun new Search-by-Target: Press Enter. '
          'Switch to Search-by-Frequency: Press \'2\'. '
          '(To exit, type \'quit\'.)')
    continue_input = check_quit(input().strip().lower())
    flag = True
    while True:
        if continue_input == '':
            flag = False
            search_by_target()
        elif continue_input == '2':
            flag = False
            search_by_freq()
        else:
            print('Could not interpret choice. Please try again.')
            continue_input = check_quit(input().strip().lower())

def search_by_freq():

    '''
    MODE 2: use an input frequency to search for nouns with similar frequencies
    '''

    os.system('cls' if os.name == 'nt' else 'clear')  # clear terminal

    print('Currently in MODE 2: Search-by-Frequency'.upper())
    print('\nTo exit the program, type \'quit\' at any time.')
    print('\nPlease enter a number (int or float) for the desired '
          'search frequency (per million):')
    search_freq = check_quit(input().strip())

    # Check if the input can be converted to a float, otherwise retry:
    flag = True
    while flag:
        try:
            search_freq = float(search_freq)
            flag = False
        except ValueError:
            print('Error: please enter a number.')
            search_freq = check_quit(input().strip())

    # Search defaults
    genders = ['masc', 'fem', 'neut']
    cases = ['nom', 'gen', 'dat', 'acc']
    numerus = ['sing', 'plu']
    length_diff = None  # not used here
    length_min = 1
    length_max = 100

    genders, cases, numerus, length_diff = search_customization(genders,
                                                                cases,
                                                                numerus,
                                                                length_diff)

    if length_diff != None:
        length_min = length_diff
        length_max = length_diff

    main_search(search_freq, length_min, length_max, genders, cases, numerus)

    print('\nRun new Search-by-Frequency: Press Enter. '
          'Switch to Search-by-Target: Press \'1\'. '
          '(To exit, type \'quit\'.)')
    continue_input = check_quit(input().strip().lower())
    flag = True
    while True:
        if continue_input == '':
            flag = False
            search_by_freq()
        elif continue_input == '1':
            flag = False
            search_by_target()
        else:
            print('Could not interpret choice. Please try again.')
            continue_input = check_quit(input().strip().lower())

def main_search(search_freq, length_min, length_max, genders, cases, numerus):

    '''
    Reads the file containing the word frequencies and extracts words
    on the basis of the specified search criteria
    '''

    print('''Searching for nouns...

        Search criteria:
        * Search frequency: {}
        * Word length: {} to {} characters
        * Genders: {}
        * Cases: {}
        * Numerus: {}
        '''.format(search_freq, length_min, length_max,
                   '/'.join(genders), '/'.join(cases), '/'.join(numerus)))

    freq_dict = dict()
    with open('deWaC_freqlist.tsv', 'r', encoding='utf-8') as F:
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

    # Transform the frequency dictionary to a list
    freq_list = []
    for word, f in freq_dict.items():
        for freq, morph_info in f.items():
            morph_all = []
            for k, m in morph_info.items():
                m = '/'.join(list(m))
                morph_all.append(m)
            # morph_all = ' '.join(morph_all)
            freq_list.append((word, freq, morph_all[0],
                              morph_all[1], morph_all[2]))
    # Reorder list by increasing difference from the target freq:
    freq_list = sorted(freq_list, key=lambda x: abs(search_freq - x[1]))
    freq_list.insert(0, ('NOUN', 'FREQUENCY', 'GENDERS', 'CASES', 'NUMERUS'))

    print('\nFound the following nouns with similar frequency:\n')
    for entry in freq_list:
        print('\t{0: <20}\t{1: <10}\t{2: <10}\t{3: <10}\t{4: <}'.format(*entry))

def search_customization(genders, cases, numerus, length_diff):

    '''
    Promts the user to enter their own search criteria
    (e.g. search only for plural nouns)
    '''

    # Search customization
    print('\nCustomize the search by changing the default search gender(s) / '
          'case(s) / word length difference / numerus?')
    print('Press \'y\' for yes, otherwise press Enter.')
    choice_custom = check_quit(input().strip().lower())
    if choice_custom != 'y':
        return genders, cases, numerus, length_diff

    print('''
    Type the desired length difference (an integer), gender(s), case(s) \
    and/or numerus, each separated by commas.
    * Options for case: nom, gen, dat, acc
    * Options for gender: masc, fem, neut
    * Options for numerus: sing OR plu
    * Options for length difference: any integer
    (not all entries are required, e.g. it is possible to enter only
    \'3, nom, acc\' to restrict the search to nominative/accusative results
    that differ from the target by 3 characters in length max.)
    ''')

    custom_input = check_quit(input().lower())
    customizations = [el.strip() for el in custom_input.split(',')]
    possible_cases = ['nom', 'gen', 'dat', 'acc']
    possible_numbers = ['sing', 'plu']
    possible_genders = ['fem', 'masc', 'neut']
    new_cases = []
    new_genders = []
    new_numbers = []
    for entry in customizations:
        try:
            new_diff = int(entry)
            length_diff = new_diff
        except:
            if entry in possible_cases:
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

    return genders, cases, numerus, length_diff

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
        print('\nTarget word not found. '
              'Press Enter to try again with another target.\n')
        check_quit(input())
        search_by_target()

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

def check_quit(some_input):
    '''
    Function to be called on every user input that checks whether
    the user wishes to quit the program
    '''
    quit_signals = ['quit', 'exit', 'q', 'e']
    if some_input in quit_signals:
        print('Exiting...\n')
        sys.exit()
    return some_input

def main():
    '''
    Main function that initializes the search
    '''

    # Select the search mode: target search or frequency search
    print('Press \'1\' to enter Search-by-Target mode or press \'2\' to enter '
          'Search-by-Frequency mode:')
    mode_input = check_quit(input().strip())

    flag = True
    while flag:
        try:
            search_mode = int(mode_input)
            flag = False
        except ValueError:
            print('Error: please type either \'1\' or \'2\'.')
            mode_input = check_quit(input().strip())

    if search_mode == 1:
        search_by_target()
    elif search_mode == 2:
        search_by_freq()

if __name__ == '__main__':

    print('\nWelcome!')

    print('\nTo exit the program, type \'quit\' and press Enter at any point.')

    # Initialize gender classifier and POS tagger
    analyzer=Analyzer(char_subs_allowed=True)

    main()
