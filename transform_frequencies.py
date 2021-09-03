'''
24 August 2021
Miriam Schulz

Script to transform the raw frequencies (token counts) in the deWaC
German frequency list (downloaded from
https://wacky.sslmit.unibo.it/doku.php?id=frequency_lists)
to frequencies per one million tokens

USAGE: python transform_frequencies.py

# Extension 25 August 2021:
Exclude nouns with a frequency per million of 0.00 to make the list smaller

## Extension 26 August 2021:
Using demorphy, additionally annotate output for gender, number and case
(create one line for each possible analysis)

'''

from demorphy import Analyzer

def get_total(filename):
    '''Get the total token count'''
    print('Starting total token occurrence count...')
    with open(filename, 'r', encoding='utf8') as F:
        total = 0
        for line in F:
            line=line.split()
            freq_raw=int(line[0])
            total += int(freq_raw)
    return total

def get_morph_analysis(word):
    '''
    Labels a word with its POS-tag (using demorphy with PTB tags, keeping only
    NN and NNS which should be common nouns);
    Gets gender, number and case information through demorphy;
    Returns a tuple containing the  morphological analysis
    (returns None if the word is not NN/NNS)
    '''
    try:
        s = demorphyAnalyzer.analyze(word)
    except KeyError:
        return 'None_found'
    morph_analyses = []
    for x in s:
        pos = x.ptb_tag
        # Exclude all non-nouns or proper nouns:
        if (pos == 'NN' or pos == 'NNS'):
            morph_analyses.append((x.gender, x.case, x.numerus))
    if len(morph_analyses) == 0:  # i.e., if the word is not NN/NNS
        return
    return morph_analyses

def transform_freqs(inputfilename, outputfilename, total):
    '''
    Transform raw frequencies to frequencies per million;
    Write to file
    '''
    print('Extracting nouns and their raw frequencies...')
    keep = []
    with open(inputfilename, 'r', encoding='utf8') as F:
        for line in F:
            line=line.split()
            if len(line) > 1:
                word=line[1]
                # to improve speed, only analyze potential nouns with demorphy:
                freq_raw=int(line[0])
                if word[0].isupper():
                    keep.append((word, freq_raw))
    keep_n = len(keep)
    print('Found {} words starting with a capital letter.'.format(keep_n))
    print('Now starting gender-numerus-case analysis...')
    i = 0  # initialize counter
    j = 0  # additional counter to keep track of untreatable words
    final_nouns = []
    unanalyzables = []
    for (word, freq_raw) in keep:
        morph_analyses = get_morph_analysis(word)  # get gender, numerus, case
        if morph_analyses == 'None_found':  # exclude unanalyzable words
            j += 1
            unanalyzables.append(word)
        elif morph_analyses != None:  # exclude non-nouns
            freq_per_million = (freq_raw / total) * 1000000
            freq_per_million = round(freq_per_million, 2)
            if freq_per_million > 0.00:  # do not keep very rare words
                for analysis in morph_analyses:
                    final_nouns.append((word, freq_per_million, freq_raw,
                                        analysis[0], analysis[1], analysis[2]))
        i += 1
        if i % 1000 == 0:
            print('  Progress: {:2.2%}'\
                  .format(i/keep_n), end='\r')

    print('\nFinished morphological analysis.')
    print('The following {} words have been skipped since they'
          'could not be morphologically analyzed:'\
           .format(j))
    for a,b,c in zip(unanalyzables[::3],unanalyzables[1::3],unanalyzables[2::3]):
        print('{:<30}{:<30}{:<}'.format(a,b,c))
    if len(unanalyzables) % 3 != 0:
        if len(unanalyzables) % 3 == 1:
            print('{:<30}'.format(unanalyzables[-1]))
        else:
            print('{:<30}{:<}'.format(unanalyzables[-2], unanalyzables[-1]))

    print('\nNow writing to file...')
    output = open(outputfilename, 'w', encoding='utf8')
    # output.write('\t'.join(['Noun', 'Freq_per_million', 'Freq_raw',
    #                         'Gender', 'Numerus', 'Case']))
    for line in final_nouns:
        output.write('\t'.join(str(el) for el in line) + '\n')
    output.close()
    print('\nDone.\n')
    return

if __name__ == '__main__':

    total = get_total('sorted.de.word.unigrams.utf8')

    demorphyAnalyzer = Analyzer(char_subs_allowed=True)

    transform_freqs('sorted.de.word.unigrams.utf8', 'deWaC_freqlist.tsv', total)
