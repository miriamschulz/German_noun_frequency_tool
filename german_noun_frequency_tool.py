'''
1 September 2021
Miriam Schulz
mschulz@coli.uni-saarland.de

Tool for stimuli creation
Version 5 – interactive version for the German deWaC noun frequency list

This script extracts nouns and their frequencies from the deWaC
word frequency list downloaded from:
https://wacky.sslmit.unibo.it/doku.php?id=frequency_lists

Nouns are morphologically analyzed using DEMorphy.
Download DEMorphy from: https://github.com/DuyguA/DEMorphy
To install DEMorphy, additionally download the words.dg file and store it
in DEMorphy's data folder, e.g. under:
anaconda3/lib/python3.6/site-packages/demorphy-1.0-py3.6.egg/demorphy/data/

USAGE: python German_noun_frequency_tool.py

MODE 1: similar noun search (Search-by-Noun)
Input: a noun
Searches for nouns that are similar to the input word in frequency,
length and morphological criteria (gender and numerus)

MODE 2: frequency search (Search-by-Frequency)
Input: a frequency (number: int or float)
Extracts all nouns with a similar frequency

Search parameters (interactively adjustable, except for word frequency):
- Word frequency:
  Depending on the frequency of the input noun (MODE 1) or the
  input frequency (MODE 2), words with compatible frequencies are returned.
  3 frequency classes are distinguished:
  * group 1: input_frequency >= 100: returns nouns with frequencies >= 100
  * group 2: 10 <= input_frequency < 100: returns nouns with a
    frequency difference of +- 5
  * group 3: input_frequency < 10: nouns with frequency difference of +- 1
- Word length: Restricts the search to nouns similar in length to the input
  noun (in MODE 1). Default value for the length difference: 2
- Morphological criteria: analysis of gender, case, numerus (using DEMorphy)
- Results are sorted by increasing frequency difference from the input noun
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

    print('{}GERMAN NOUN FREQUENCY TOOL{}\n'.format(heading_col, reset_col))

    print('{}Please enter either\n'
          '- a noun (e.g. Haus), or\n'
          '- a search frequency (int or float, e.g. 5.5){}'\
          .format(input_col, reset_col))
    user_input = check_input(input().strip())
    if user_input == '' or user_input == 'v' or user_input == 'c':
        print('\n{}Please enter a valid noun or search frequency.\n'
              'Press Enter to try again with another noun or frequency.{}'\
              .format(warn_col, reset_col))
        choice = check_input(input().strip())
        start_search()

    # Differentiate between frequency and word input:
    try:
        search_freq = float(user_input)
        # Set search defaults
        genders = {'masc', 'fem', 'neut'}
        length_min = 1
        length_max = 100
        print('\nEntered search frequency: {} per million'.format(search_freq))
    except ValueError:
        target_word = user_input
        target_freq = get_target_freq(target_word)
        t_genders, t_cases, t_nums = get_target_morph(target_word)
        print('\nAnalysis of the input noun \'{}\':'.format(target_word))
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
    cases = {'dat', 'acc'}
    numerus = {'sing'}

    # Print search criteria
    print('\nThe automatically defined criteria for your search are:')
    print('\t* Search frequency:\t', end='')
    frequency_range(search_freq)
    print('\t* Word length:\t\t{} to {} characters'\
          .format(length_min, length_max))
    print('\t* Gender(s):\t\t{}'.format(', '.join(genders)))
    print('\t* Case(s):\t\t{}'.format(', '.join(cases)))
    print('\t* Numerus:\t\t{}'.format(', '.join(numerus)))
    print('{}\nPress \'c\' to change these criteria, otherwise press Enter.{}'
          .format(input_col, reset_col))
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

    print('\nSearching for nouns...')

    freq_dict = dict()
    i = 0
    n = len(noun_freq_dict.keys())
    for freq, noundict in noun_freq_dict.items():
        freq_eval = frequency_check(search_freq, freq)
        if freq_eval == True:
            for noun, morphinfo in noundict.items():
                # Check length
                if length_min <= len(noun) <= length_max:
                    # Check for overlap of morphological criteria
                    noun_genders = morphinfo['gender']
                    noun_cases = morphinfo['case']
                    noun_num = morphinfo['numerus']
                    shared_genders = genders & noun_genders
                    shared_cases = cases & noun_cases
                    shared_nums = numerus & noun_num
                    # Update the frequency dictionary if any overlap is found
                    if shared_genders and shared_cases and shared_nums:
                        if noun in freq_dict.keys():
                            if freq in freq_dict[noun].keys():
                                print("DUPLICATE")
                            else:
                                freq_dict[noun][freq]={'gender':shared_genders,
                                                       'case':shared_cases,
                                                       'numerus':shared_nums}
                        else:
                            freq_dict[noun] = dict()
                            freq_dict[noun][freq]={'gender':shared_genders,
                                                   'case':shared_cases,
                                                   'numerus':shared_nums}
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

    possible_cases = {'nom', 'gen', 'dat', 'acc'}
    possible_numbers = {'sing', 'plu'}
    possible_genders = {'fem', 'masc', 'neut'}

    choice_custom = check_input(input().strip().lower())
    if choice_custom != 'c':
        return genders, cases, numerus, length_min, length_max

    print('\nSEARCH CUSTOMIZATION OPTIONS:')
    print('\t*  LENGTH RANGE:\te.g. \'8-10\' for words of '
          '8 to 10 characters in length')
    print('\t*  CASE:\t\tnom, gen, dat, acc')
    print('\t*  GENDER:\t\tmasc, fem, neut')
    print('\t*  NUMERUS:\t\tsing OR plu')
    print('\t*  Remove all search filters: simply type \'all\'')
    print('(Not all entries are required; it is possible to enter only e.g.\n'
          '\'3-5, masc, neut\' to restrict the search to masculine or neutrum\n'
          'nouns with a word length of 3 to 5 characters.)')

    print('\n{}Type the desired word length range, gender(s), case(s) '
          'and/or numerus.'
          '\nSeparate each entry by a comma.{}'\
          .format(input_col, reset_col))

    custom_input = check_input(input().lower())
    customizations = [el.strip() for el in custom_input.split(',')]

    if 'all' in customizations:
        return possible_genders, possible_cases, possible_numbers, 1, 100

    new_cases = set()
    new_genders = set()
    new_numbers = set()
    for entry in customizations:
        if '-' in entry:
            length_min, length_max = entry.split('-')
            try:
                length_min = int(length_min)
                length_max = int(length_max)
            except:
                pass
        elif entry in possible_cases:
            new_cases.add(entry)
        elif entry in possible_numbers:
            new_numbers.add(entry)
        elif entry in possible_genders:
            new_genders.add(entry)
    if new_cases != set():
        cases = new_cases
    if new_genders != set():
        genders = new_genders
    if new_numbers != set():
        numerus = new_numbers

    return genders, cases, numerus, length_min, length_max

def frequency_check(target_freq, freq):
    '''
    Evaluates a noun's frequency against the frequency of the target noun.
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

def frequency_range(freq):
    '''
    Prints the frequency ranges for a search given an input search frequency
    '''
    if (freq < 10):
        print('{} to {} per million'\
              .format(max(round(freq-1, 2), 0), round(freq+1, 2)))
    elif (freq >= 100):
        print('100+ per million')
    else:  # i.e., if 10 <= search_freq < 100
        if freq-5 >= 10:
            print('{} to {} per million'\
                  .format(round(freq-5, 2), round(freq+5, 2)))
        elif freq-1 < 10:
            print('{} to {} per million'\
                  .format(round(freq-1, 2), round(freq+5, 2)))
        else:
            print('{} to {} per million'.format(10.0, round(freq+5, 2)))
    return

def add_to_dict(noun_freq_dict, freq, noun, gender, case, num, create):
    if create == True:
        noun_freq_dict[freq][noun] = dict()
        noun_freq_dict[freq][noun]['gender'] = set()
        noun_freq_dict[freq][noun]['case'] = set()
        noun_freq_dict[freq][noun]['numerus'] = set()
    noun_freq_dict[freq][noun]['gender'].add(gender)
    noun_freq_dict[freq][noun]['case'].add(case)
    noun_freq_dict[freq][noun]['numerus'].add(num)
    return noun_freq_dict

def read_nouns(filename):
    '''
    Pre-load the nouns and store them in a dictionary structure
    for rapid access
    '''
    noun_freq_dict = dict()
    with open(filename, 'r', encoding='utf-8') as F:
        i = 0
        n = 1974122  # total lines in deWaC_freqlist.tsv
        for line in F:
            line=line.split()
            noun=line[0]
            freq=float(line[1])
            gender=line[3]
            case=line[4]
            num=line[5]
            if freq in noun_freq_dict.keys():
                if noun in noun_freq_dict[freq].keys():
                    noun_freq_dict = add_to_dict(noun_freq_dict, freq, noun,
                                                 gender, case, num, False)
                else:
                    noun_freq_dict = add_to_dict(noun_freq_dict, freq, noun,
                                                 gender, case, num, True)
            else:
                noun_freq_dict[freq] = dict()
                noun_freq_dict = add_to_dict(noun_freq_dict, freq, noun,
                                             gender, case, num, True)
            i += 1
            if i % 1000 == 0:
                print(' (1/2) Reading in nouns. Progress: {:2.0%}'\
                      .format(i/n), end='\r')
    return noun_freq_dict

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
        print('\n{}Noun not found. '
              'Press Enter to try again with another noun or frequency.{}'\
              .format(warn_col, reset_col))
        choice = check_input(input().strip())
        start_search()

def get_target_morph(noun):
    '''
    Extracts the possible genders, cases and numbers of the input target word
    '''
    s = analyzer.analyze(noun)
    genders = set()
    cases = set()
    numbers = set()
    for x in s:
        genders.add(x.gender)
        cases.add(x.case)
        numbers.add(x.numerus)
    return genders, cases, numbers

def read_verbs(filename):
    '''
    Pre-load the noun-verb bigrams and store them in a dictionary structure
    for rapid access
    '''
    print()
    verb_dict = dict()
    i = 0
    # number of lines in bigram file (3306296) plus manually added bigrams
    # (manually added verbs: öffnen, befestigen, eilen, schauen, herausholen,
    # festhalten, schneiden, essen, besteigen, reingehen, hineingehen,
    # aufschlagen, kochen
    n_bigrams = 3306296 + 9981 + 3044 + 1567 + 2374 + 492 + 2813 + 1191 + 3808\
                + 835 + 52 + 180 + 369 + 699
    with open(filename, 'r', encoding='utf-8') as F:
        for line in F:
            line = line.split('\t')
            i += 1
            if i % 100 == 0:
                print(' (2/2) Reading in noun-verb bigrams. Progress: {:2.0%}'\
                      .format(i/n_bigrams), end='\r')
            bigram_count = line[0]
            noun = line[1].title()
            noun_pos = line[2]
            verb = line[3]
            verb_pos = line[4]
            try:
                verb_dict[verb].append((noun, bigram_count))
            except:
                verb_dict[verb] = [(noun, bigram_count)]
    return verb_dict

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

    # If no verb is entered, start again
    if target_verb == '' or target_verb == 'v' or target_verb == 'c':
        print('\n{}Input is not a verb.{}'\
              .format(warn_col, reset_col))
        continue_options(freq_list)

    keep_bigrams = []
    if target_verb in verb_dict.keys():
        for (noun, bigram_count) in verb_dict[target_verb]:
            if noun in freq_dict.keys():
                freq = freq_dict[noun][0]
                genders = freq_dict[noun][1]
                cases = freq_dict[noun][2]
                nums = freq_dict[noun][3]
                keep_bigrams.append((bigram_count, noun, freq,
                                     genders, cases, nums))
        # Print search results
        if len(keep_bigrams) > 0:
            print('\n\nOut of the {} search results, {} nouns can occur with '
                  '\'{}\':\n'\
                  .format(len(freq_list), len(keep_bigrams), target_verb))
            formatting_pattern='{0:^14}|{1:<25}|{2:^13}|{3:^20}|{4:^20}|{5:^12}'
            print('\t'+formatting_pattern.format('BIGRAM COUNT',
                                                 '           NOUN',
                                                 'FREQUENCY', 'GENDERS',
                                                 'CASES', 'NUMERUS'))
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
            print('\n{}None of the search nouns are attested with \'{}\'.{}'\
                  .format(warn_col, target_verb, reset_col))
    else:
        print('\n{}The verb {} is not present in the bigram file.\n'
              'To add it, use the script bigram_extractor_manual.py.{}'\
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
    heading_col = '\u001b[30;1m'      # bright black
    warn_col = '\u001b[31;1m'         # bright red
    input_col = '\u001b[36;1m'        # bright cyan
    sun_col = '\u001b[38;5;11m'       # bright pink
    exit_col = '\u001b[35;1m'         # bright dark blue
    reset_col = '\u001b[0m'           # reset to normal

    # os.system('cls' if os.name == 'nt' else 'clear')  # clear terminal

    # Welcome message
    print('\n\n{}Welcome!{}'.format(heading_col, reset_col))
    print('{}  \\ /'.format(sun_col))
    print(' – o –')
    print('  / \\{}'.format(reset_col))

    # Instructions / About
    print('\nThis program lets you search the deWaC German noun frequency list')
    print('(https://wacky.sslmit.unibo.it/doku.php?id=frequency_lists')
    print('to find German nouns by their frequency, length, and')
    print('morphological criteria (gender, case and numerus).')
    print('\nInitializing, please wait...')

    # Initialize gender classifier and POS tagger
    analyzer = Analyzer(char_subs_allowed=True)

    # Read in the verb bigram file and the noun file
    noun_freq_dict = read_nouns('deWaC_freqlist.tsv')
    verb_dict = read_verbs('bigrams_noun_verb_freq2+.tsv')

    # Start prompt
    print('\n\n{}Finished initialization. Press Enter to start.{}'\
          .format(input_col, reset_col))
    print('\n{}To exit the program, simply type \'quit\' or \'q\' '
          'followed by Enter at any point.{}'\
          .format(exit_col, reset_col))

    start = check_input(input().strip())

    # Begin search
    start_search()
