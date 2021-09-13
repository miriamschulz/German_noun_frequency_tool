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

MODE 1: similar target search (Search-by-Target)
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
  (lemmatized) is >= 1)

'''

import sys
import os
from demorphy import Analyzer


def search_by_target():

    '''
    MODE 1: use an input noun to search for similar nouns
    '''

    os.system('cls' if os.name == 'nt' else 'clear')  # clear terminal

    current_mode = 1
    print('{}Currently in MODE 1: Search-by-Target{}'.upper()\
          .format(heading_col, reset_col))
    print('\nTo exit the program, type \'quit\' or \'q\' at any time.')
    print('To switch to Search-by-Frequency mode, press \'s\'.')
    print('\n{}Please enter a target word:{}'\
          .format(input_col, reset_col), end=' ')
    target_word = check_input(input().strip(), current_mode)
    target_freq = get_target_freq(target_word)
    t_genders, t_cases, t_nums = get_target_morph(target_word)
    print('\n\tChosen target: \t\t\'{}\''.format(target_word))
    print('\tFrequency rank: \t{} per million'.format(target_freq))
    print('\tWord length: \t\t{} characters'.format(len(target_word)))
    print('\tPossible genders: \t{}'.format(', '.join(t_genders)))
    print('\tPossible cases: \t{}'.format(', '.join(t_cases)))
    print('\tPossible numerus: \t{}'.format(', '.join(t_nums)))

    # Define search defaults
    cases = ['dat', 'acc']
    numerus = ['sing']
    length_diff = 2
    length_min = len(target_word) - length_diff
    if length_min <= 0:
        length_min = 1
    length_max = len(target_word) + length_diff

    # Customize search
    genders, cases, numerus, length_min, length_max = \
        search_customization(t_genders, cases, numerus, length_min, length_max,
                             current_mode)

    # Search for similar targets
    freq_list = main_search(target_freq, length_min, length_max,
                            genders, cases, numerus)

    continue_options(current_mode, freq_list)

def search_by_freq():

    '''
    MODE 2: use an input frequency to search for nouns with similar frequencies
    '''

    os.system('cls' if os.name == 'nt' else 'clear')  # clear terminal

    current_mode = 2
    print('{}Currently in MODE 2: Search-by-Frequency{}'.upper()\
          .format(heading_col, reset_col))
    print('\nTo exit the program, type \'quit\' at any time.')
    print('To switch to Search-by-Target mode, press \'s\'.')
    print('\n{}Please enter a number (int or float) for the desired '
          'search frequency (per million):{}'\
          .format(input_col, reset_col), end=' ')
    search_freq = check_input(input().strip(), current_mode)

    # Check if the input can be converted to a float, otherwise retry:
    flag = True
    while flag:
        try:
            search_freq = float(search_freq)
            flag = False
        except ValueError:
            print('{}Error: please enter a number. Try again:{}'\
                  .format(warn_col, reset_col), end=' ')
            search_freq = check_input(input().strip(), current_mode)

    # Set search defaults
    genders = ['masc', 'fem', 'neut']
    cases = ['dat', 'acc']
    numerus = ['sing']
    length_min = 1
    length_max = 100

    # Customize search
    genders, cases, numerus, length_min, length_max = \
        search_customization(genders, cases, numerus, length_min, length_max,
                             current_mode)

    freq_list = main_search(search_freq, length_min, length_max,
                            genders, cases, numerus)

    continue_options(current_mode, freq_list)

def main_search(search_freq, length_min, length_max, genders, cases, numerus):

    '''
    Reads the file containing the word frequencies and extracts+prints words
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
            if i % 1000 == 0:
                print(' Progress: {:2.0%}'.format(i/n), end='\r')
            i += 1
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
                        length_min, length_max, current_mode):

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
    choice_custom = check_input(input().strip().lower(), current_mode)
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

    custom_input = check_input(input().lower(), current_mode)
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
              'Press Enter to try again with another target '
              'or press \'s\' to switch to Search-by-Frequency.{}'\
              .format(warn_col, reset_col))
        choice = check_input(input().strip(), None)
        if choice.lower() == 's':
            search_by_freq()
        else:
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

def bigram_search(freq_list, current_mode):
    '''
    Checks whether the nouns found in the main search occur with an
    input verb in the lemmatized deWaC bigram list
    '''
    print('\n{}Please enter a target verb (infinitive) to check for '
          'co-occurrence with the retrieved nouns:{}'\
          .format(input_col, reset_col), end=' ')
    target_verb = check_input(input().strip(), current_mode)
    target_verb = target_verb.lower()
    keep_bigrams = []
    with open('bigrams_noun_verb_12verbs.tsv', 'r', encoding='utf-8') as F:
        for line in F:
            line = line.split('\t')
            bigram_count = line[0]
            noun = line[1]
            noun_pos = line[2]
            verb = line[3]
            verb_pos = line[4]
            if verb == target_verb:
                for n in freq_list:
                    word = n[0]
                    if noun == word.lower():  #TODO: lemmatize the noun?
                        word_freq = n[1]
                        genders = n[2]
                        cases = n[3]
                        nums = n[4]
                        keep_bigrams.append((bigram_count, word, word_freq,
                                             genders, cases, nums))
    # Print search results
    if len(keep_bigrams) > 0:
        print('\nOut of the {} search results, {} nouns can occur with \'{}\':\n'\
              .format(len(freq_list), len(keep_bigrams), target_verb))
        formatting_pattern = '{0: ^14}|{1: <25}|{2: ^13}|{3: ^20}|{4: ^20}|{5: ^12}'
        print('\t' + formatting_pattern.format('BIGRAM COUNT', '           NOUN',
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
    continue_options(current_mode, freq_list)

def continue_options(current_mode, freq_list):
    if current_mode == 1:
        current_search_mode = 'Search-by-Target'
        other_search_mode = 'Search-by-Frequency'
    else:
        current_search_mode = 'Search-by-Target'
        other_search_mode = 'Search-by-Frequency'
    print('\nRun new {}: press {}Enter{}'\
          .format(current_search_mode, input_col, reset_col))
    print('Switch to {}: press {}\'s\'{}'\
          .format(other_search_mode, input_col, reset_col))
    print('To check which of the nouns can follow a specific target verb:'
          ' press {}\'v\'{}'.format(input_col, reset_col))
    print('To exit, type {}\'quit\' or \'q\'.{}'\
          .format(input_col, reset_col), end=' ')
    continue_input = check_input(input().strip().lower(), current_mode)
    flag = True
    while True:
        if continue_input == '':
            flag = False
            if current_mode == 1:
                search_by_target()
            else:
                search_by_freq()
        elif continue_input == 'v':
            bigram_search(freq_list, current_mode)
        else:
            print('{}Could not interpret choice. Please try again.{}'\
                  .format(warn_col, reset_col))
            continue_input = check_input(input().strip().lower(), current_mode)

def check_input(some_input, current_mode):
    '''
    Function to be called on every user input that checks whether
    the user wishes to quit the program
    '''
    quit_signals = ['quit', 'exit', 'q', 'e']
    if some_input in quit_signals:
        print('\n{}Exiting...{}\n'.format(exit_col, reset_col))
        sys.exit()
    elif some_input.lower() == 's':
        if current_mode == 1:
            search_by_freq()
        elif current_mode == 2:
            search_by_target()
    return some_input

def main():
    '''
    Main function that initializes the search
    '''

    # Select the search mode: target search or frequency search
    print('\n{}Press \'1\' to enter Search-by-Target mode or press \'2\' to '
          'enter Search-by-Frequency mode:{}'.format(input_col, reset_col),
          end=' ')
    mode_input = check_input(input().strip(), None)

    flag = True
    while flag:
        try:
            search_mode = int(mode_input)
            if (search_mode == 1) or (search_mode == 2):
                flag = False
            else:
                print('{}Error: please type either \'1\' or \'2\'.{}'\
                      .format(warn_col, reset_col))
                mode_input = check_input(input().strip(), None)
        except ValueError:
            print('{}Error: please type either \'1\' or \'2\'.{}'\
                  .format(warn_col, reset_col))
            mode_input = check_input(input().strip(), None)

    if search_mode == 1:
        search_by_target()
    elif search_mode == 2:
        search_by_freq()

if __name__ == '__main__':

    # Define colors for warnings etc.
    # back_lightgrey = '\u001b[48;5;254m'
    # back_grey = '\u001b[47m'
    # back_lilac = '\u001b[48;5;189m'
    back_search = '\u001b[48;5;195m'  # light blue
    back_verbs = '\u001b[48;5;230m'   # light yellow
    heading_col = '\u001b[30;1m'  # bright black
    warn_col = '\u001b[31;1m'     # bright red
    input_col = '\u001b[36;1m'    # bright cyan
    sun_col = '\u001b[38;5;11m'   # bright pink
    exit_col = '\u001b[35;1m'     # bright dark blue
    reset_col = '\u001b[0m'

    os.system('cls' if os.name == 'nt' else 'clear')  # clear terminal

    print('{}Welcome!{}'.format(heading_col, reset_col))
    print('{}  \\ /'.format(sun_col))
    print(' – o –')
    print('  / \\{}'.format(reset_col))

    print('\nThis program lets you search the deWaC German noun frequency list')
    print('(https://wacky.sslmit.unibo.it/doku.php?id=frequency_lists')
    print('to find German nouns by their frequency, length, and')
    print('morphological criteria (gender, case and numerus).')

    print('\nTo exit the program, simply type \'quit\' or \'q\' '
          'followed by Enter at any point.')

    # Initialize gender classifier and POS tagger
    analyzer=Analyzer(char_subs_allowed=True)

    main()
