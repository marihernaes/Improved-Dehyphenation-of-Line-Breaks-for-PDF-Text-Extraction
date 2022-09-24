# Copyright 2019, University of Freiburg,
# Chair of Algorithms and Data Structures.
# Author: Mari Hernaes.
"""
For a file in the format <HYHPENATED SENTENCE>tab<ORIGINAL SENTENCE>, extract
the hyphenated words and create a corpus on which a model can train on.
The output is a corpus in the format <LABEL>tab<PREFIX>tab<SUFFIX>
"""

import sys
import re

# ============================================================================

# The character used to represent the special hyphen symbol
HYPHENATION_SYMBOL = '\u0387'

# ============================================================================


def run(input_file, output_file):
    """Reads the hyphenated file. Extracts real and fake hyphenations, and
    writes these to the output file with the correct label"""
    hyphen_symbol = '\u0387'
    is_true_hyphen = True  # Flag to detect true hyphens (should be kept)

    num_lines = sum(1 for line in open(input_file))
    line_counter = 0
    with open(input_file) as input:
        with open(output_file, 'w') as output:
            for line in input:
                # Print some progress
                line_counter += 1
                printProgressBar(line_counter, num_lines, length=50)

                # Each line is <hyphenated sentence>TAB<original sentence>
                line = line.split('\t')
                if len(line) < 2:
                    print('Warning: data set format not correct')

                # Split the sentences to lists of words
                input_words = line[0].strip().split()
                expected_words = line[1].strip().split()

                for i, word in enumerate(input_words):
                    # Find words with custom hyphens
                    if re.search(r'[\S]+(?:%s[\S]+)+' % hyphen_symbol, word):
                        # Compare the hyphenated word with the original one
                        if expected_words[i].lower() == word.replace(
                                                   hyphen_symbol, '-').lower():
                            is_true_hyphen = True
                        else:
                            is_true_hyphen = False

                        (prefix, suffix) = word.split(hyphen_symbol)
                        label = '1' if is_true_hyphen else '0'
                    else:
                        # If there are no hyphens
                        continue

                    # Write label and word to output file
                    output.write('{}\t{}\t{}\n'.format(label, prefix, suffix))


def printProgressBar(iteration, total, length=100, fill='█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(1) + "f}").format(
               100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % ('', bar, percent, 'Complete'), end='\r')
    # Print New Line on Complete
    if iteration == total:
        print()


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("""Usage: python3 create_corpus.py"""
              """ <hyphenated_file.txt> <corpus_file> """)
        sys.exit()

    input = sys.argv[1]
    output = sys.argv[2]

    sys.stdout.write("\nProcessing file: %s \n" % (input))
    run(input, output)
    sys.stdout.write("Done.\n")
