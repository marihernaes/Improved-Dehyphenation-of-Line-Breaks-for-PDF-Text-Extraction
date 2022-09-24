# Copyright 2019, University of Freiburg,
# Chair of Algorithms and Data Structures.
# Author: Mari Hernaes.

import sys
import re
import time
import os
import glob
from pathlib import Path
import hyphenate_sentence as hs
import reformat_ontonotes
import reformat_clueweb
import reformat_wikipedia


class ProcessHyphenation:
    """ A class to control the hyphenation process of a data set."""

    def __init__(self):
        """ Constructor """
        self.hyphenate = None
        self.reformat = None

    def load_hyphenate_sentence(self, hyphen_dist=False):
        """ Loads the hyphenate sentence class """
        self.hyphenate = hs.HyphenateSentence() if not hyphen_dist \
            else hs.HyphenateSentence(hyphen_dist)

    def load_ontonoes(self):
        """ Loads the clueweb reformat class """
        self.reformat = reformat_ontonotes.ReformatOntonotes()

    def load_clueweb(self):
        """ Loads the clueweb reformat class """
        self.reformat = reformat_clueweb.ReformatClueweb()

    def load_wikipedia(self):
        """ Loads the wikipedia reformat class """
        self.reformat = reformat_wikipedia.ReformatWikipedia()

    def process_file(self, input_file, output_file):
        """
        Processes a file. Reads the input, runs methods to clean, normalize and
        hyphenate the sentences, and writes the result to an output file.

        The reformat classes each have a method 'readline', which returns a
        'normal' sentence (a sentence without POS tags and such). This implies,
        though, that the data set in the input file is structured with one
        example sentence pro line.
        """
        counter_lines = 0
        counter_ignored_lines = 0

        num_lines = sum(1 for line in open(input_file))
        with open(input_file) as inp:
            with open(output_file, 'w') as out:
                for line in inp:
                    if not line.strip():
                        continue  # If the line is empty

                    # Print some progress
                    counter_lines += 1
                    self.printProgressBar(counter_lines, num_lines, length=50)

                    raw_sentence = self.reformat.read_line(line.strip())

                    if self.check_language(raw_sentence) is False:
                        counter_ignored_lines += 1
                        continue  # If the language is non-latin

                    # Hyphenate the normalized sentence
                    normalized_sentence = self.normalize_sentence(raw_sentence)
                    hyphenated_sentence = \
                        self.hyphenate.hyphenate_sentence(normalized_sentence)

                    # And write it to the output file
                    out.write('{}\t{}\n'.format(
                        hyphenated_sentence, normalized_sentence))

        print('{} of {} lines ignored ({:.2f}%)'.format(
            counter_ignored_lines, counter_lines,
            (counter_ignored_lines/counter_lines)*100))

    def check_language(self, sentence):
        """
        Checks if a sentence has non-latin characters. Returns boolean.

        >>> ph = ProcessHyphenation()
        >>> ph.check_language("Don't you want to see Tom?")
        True
        >>> ph.check_language("Você não quer ver o Tom?")  # Portuguese
        True
        >>> ph.check_language("Ты не хочешь увидеться с Томом?")  # Russian
        False
        >>> ph.check_language("Δεν θέλεις να δεις τον Τομ")  # Greek
        False
        >>> ph.check_language("டாமைப் பார்க்க வேண்டாமா?")  # Tamil
        False
        """

        # Check for character in the range 'greek and coptic' to 'greek extend'
        return False if re.search(u'[\u0370-\u1fff]', "u'%s'" % sentence) \
            else True

    def normalize_sentence(self, sentence):
        """
        Normalizes a raw sentence (stripped, without POS or NER tags).

        Returns a sentence without links, and with a normalized format for
        hyphenations, and/or dashes, etc.

        >>> ph = ProcessHyphenation()
        >>> ph.normalize_sentence('Well you can choose this/that/there/here')
        'Well you can choose this / that / there / here'
        >>> ph.normalize_sentence("This is web.com, e-mail me at me@mail.com")
        'This is x e-mail me at x'
        """

        # Replace links and similar (words with '.', '@' or ':') with 'x'
        sentence = re.sub(r'\s*\S+[.@:]\S+', ' x', sentence)

        # Insert spaces around slashes which are directly between two words
        if re.search(r'\w/\w', "u'%s'" % sentence):
            dash_indexes = [d.start() for d in re.finditer('/', sentence)]
            # Iterate from end of index list (to avoid indexing issues)
            for i in reversed(dash_indexes):
                # Insert spaces
                sentence = sentence[:i] + ' / ' + sentence[i + 1:]

        # Ignore soft hyphenation marks
        sentence = re.sub(u'[\u00ad]', '', sentence)
        return sentence

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
    if len(sys.argv) < 3 or len(sys.argv) > 5:
        print("""Usage: python3 process_hyphenation.py """
              """<input data directory> <output data directory> """
              """<'c' for clueweb, 'o' for ontonotes, 'w' for wikipedia> """
              """<optional: int (hyphen_dist)>""")
        sys.exit()

    input_directory = sys.argv[1]
    output_directory = sys.argv[2]
    data_set_type = sys.argv[3]
    if not (data_set_type == 'c' or data_set_type == 'o' or
            data_set_type == 'w'):
        print('Data set type should be c or o or w!')
        sys.exit()

    ph = ProcessHyphenation()

    # Read the hyphen distance, if specified
    hyphen_dist = False
    if len(sys.argv) > 3:
        try:
            hyphen_dist = int(sys.argv[4])
        except ValueError:
            sys.stdout.write("\nHyphen distance not an integer")

    # Load the proper classes
    ph.load_hyphenate_sentence(hyphen_dist) if hyphen_dist else \
        ph.load_hyphenate_sentence()

    if data_set_type == 'c':
        ph.load_clueweb()
    elif data_set_type == 'o':
        ph.load_ontonoes()
    elif data_set_type == 'w':
        ph.load_wikipedia()

    sys.stdout.write("\nProcessing with hyphens per %d word..\n\n" %
                     ph.hyphenate.hyphen_distance)

    # Fetch the files from the input directory
    input_file_list = []
    if data_set_type == 'c':
        input_file_list = sorted(
            glob.glob(input_directory + "*.txt"), reverse=True)
    elif data_set_type == 'w':
        input_file_list = sorted(
            glob.glob(input_directory + "*.txt"), reverse=True)
    elif data_set_type == 'o':
        for path, dirs, files in os.walk(input_directory):
            for name in files:
                input_file_list.append(os.path.join(path, name))
    else:
        print('Warning. Data set type not recognized.')
        sys.exit()
    if not input_file_list:
        print('Warning. No input files found.')
        sys.exit()
    sys.stdout.write("\nOrder of files: %s\n" % input_file_list)

    total_time = 0
    for input_file in input_file_list:
        sys.stdout.write("\nFile to be processed: %s\n" % input_file)
        start = time.time()

        # Do not include subfolders in the hyphenated output
        folder = input_file.split("/")
        output_name = folder[-1][:-4] + '-hyphenated.tsv'
        if len(folder) > 2:
            # Include the subfolder names to avoid duplicates
            output_name = folder[-3] + folder[-2] + output_name

        # Create the hyphenated filename
        output_file = output_directory + output_name
        # Do not overwrite output files
        if Path(output_file).is_file():
            sys.stdout.write("File already written.\n\n")
            continue

        ph.process_file(input_file, output_file)

        stop = time.time()
        sys.stdout.write("File done. (%.3f)\n\n" % (stop - start))
        total_time += stop - start

    sys.stdout.write("All done. (%.3f)\n\n" % total_time)
