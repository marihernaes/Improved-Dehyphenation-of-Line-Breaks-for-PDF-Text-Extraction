# Copyright 2019, University of Freiburg,
# Chair of Algorithms and Data Structures.
# Author: Mari Hernaes.

import sys
import re
import glob
import time


class CreateVocabulary:
    """A class to create a vocabulary, based on a text data set"""

    def __init__(self, digit_symobl='\u03A7'):
        """ Constructor. For digits, save a special symbol """
        self.word_vocabulary = {}
        self.digit_symbol = digit_symobl  # Must be a character symbol
        if re.search('\\w', self.digit_symbol) is None:
            raise ValueError('The digit symbol must be in range <a-zA-Z0-9>')

    def process_file(self, input_file):
        """
        Read a text data set and add words to an internal vocabulary.
        The data set is in the format <hyphenated sentence> TAB <original>.
        Only add the words from the original sentence.
        """
        line_counter = 0

        num_lines = sum(1 for line in open(input_file))
        with open(input_file) as inp:
            for line in inp:
                # Print some progress
                line_counter += 1
                self.printProgressBar(line_counter, num_lines, length=50)
                try:
                    (_, sentence) = line.strip().split('\t')
                except Exception:
                    print('Warning: input file format wrong')
                    print('Should be <hyphenated sentence>tab<original>')
                for word in sentence.split():
                    self.add_word_to_vocabulary(word)

    def add_word_to_vocabulary(self, word):
        """
        Add a word to the intern vocabulary. Do not add normal digits, but the
        word with the special digit symbol.

        >>> c = CreateVocabulary('_')
        >>> c.add_word_to_vocabulary('hello')
        >>> sorted(c.word_vocabulary.items())
        [('hello', 1)]
        >>> c.add_word_to_vocabulary('4-million-dollar')
        >>> c.add_word_to_vocabulary('5-million-dollar')
        >>> sorted(c.word_vocabulary.items())
        [('_-million-dollar', 2), ('hello', 1)]
        """
        # Check if the word is valid
        if self.check_word(word):
            # If the word has digits, replace them with special digit symbol
            word = re.sub(r'[0-9]', self.digit_symbol, word)
            # Lowercase it
            word = word.lower()
            if word in self.word_vocabulary:
                self.word_vocabulary[word] += 1  # Increase frequency
            else:
                self.word_vocabulary[word] = 1  # Or add for the first time

    def check_word(self, word):
        """
        Checks if a word does not have special characters, double hyphens or
        similar.

        >>> c = CreateVocabulary('_')
        >>> c.check_word('15-million')
        True
        >>> c.check_word('well--that')
        False
        >>> c.check_word('&4§1')
        False
        """

        # The word should include at least one normal letter
        if re.search(r'[a-zA-Z]', word) is None:
            return False

        # The hyphens should not be the very first or last character, or double
        pattern = re.compile('^\\w+(-{0,1}\\w+)*$')
        if pattern.match(word):
            return True

        return False

    def printProgressBar(self, iteration, total, length=100, fill='█'):
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


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("""Usage: python3 create_vocabulary.py"""
              """ <hyphenated dataset directory> <vocabulary file name>"""
              """ <int, frequency threshold> """)
        sys.exit()

    input_directory = sys.argv[1]
    output_file = sys.argv[2]
    try:
        frequency_threshold = int(sys.argv[3])
    except ValueError as err:
        print(err)
        sys.exit()

    # Fetch the input file names
    input_file_list = glob.glob(input_directory + "*hyphenated.txt")
    sys.stdout.write("\nFiles to be processed: %s" % input_file_list)

    # Fill the vocabulary
    cd = CreateVocabulary()
    total_start = time.time()
    for input_file in input_file_list:
        start = time.time()
        sys.stdout.write("\nAdding words from: %s" % input_file)
        cd.process_file(input_file)
        stop = time.time()
        sys.stdout.write("\nDone. (%.4f)" % (stop - start))

        # Sort the words by frequency, in descending order
        sorted_word_vocabulary = sorted(
            cd.word_vocabulary.items(), key=lambda x: -x[1])

        # Write the vocabulary
        start = time.time()
        with open(output_file, 'w') as output:
            sys.stdout.write("\nWriting vocabulary to file: %s" % output_file)
            sys.stdout.write("\nFrequency threshold %d" % frequency_threshold)
            for i, (word, frequency) in enumerate(sorted_word_vocabulary):
                if frequency < frequency_threshold:
                    sys.stdout.write('\nFrequency threshold reached.')
                    sys.stdout.write('\n%d words written.' % i)
                    break
                output.write('%d\t%s\n' % (word, frequency))
            if frequency_threshold < 2:
                # For freqency thresholds less than 2, all words are written
                sys.stdout.write(
                    '\n%d words written.' % len(sorted_word_vocabulary))
            stop = time.time()
            sys.stdout.write("\nDone. (%.4f)" % (stop - start))

    total_stop = time.time()
    sys.stdout.write("\nAll done. (%.4f)\n" % (total_stop - total_start))
