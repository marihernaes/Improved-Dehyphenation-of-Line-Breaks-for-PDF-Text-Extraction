# Copyright 2019, University of Freiburg,
# Chair of Algorithms and Data Structures.
# Author: Mari Hernaes.

import merge_hyphens_baseline
import merge_hyphens_baseline_with_supplements as mhbsuppl
import crf_predict as c
import language_model_predict as languagemodel
import re
import sys


class ProcessFile:
    """ Class to run a model on a given hyphenated data set """

    def __init__(self, model_type, hyphen_symbol='\u0387'):
        """ Initializes with a given hyphen symbol """
        # The character used to represent a hyphenation position in a word.
        self.hyphen_sym = hyphen_symbol
        self.model_type = model_type
        self.model = None

    def load_basic_baseline(self, word_list):
        """ Prepares the baseline by loading the dictionary."""
        self.model = merge_hyphens_baseline.MergeHyphensBaseline(
            word_list, self.hyphen_sym)

    def load_baseline_with_supplements(self, word_list):
        """ Prepares the supplemented baseline by loading the dictionary."""
        self.model = mhbsuppl.BaselineWithSupplements(
            word_list, self.hyphen_sym)

    def load_linear_regression(self, model_file):
        """ Loads the machine learning model """
        linreg = c.CrfPredict(self.hyphen_sym)
        linreg.load_model_file(model_file)
        self.model = linreg

    def run(self, hyphenated_file, result_file):
        """
        For a dataset of hyphenated sentences in the format
        <hyphenated sentence>tab<original sentence>, use the given model to
        find out if the hyphen should stay or not.

        The model is either 'baseline', 'baseline_supplemented',
        'linear-regression', or 'language-model'.

        The output is a file in the format
        <hyphenated sentence>tab<output sentence>.

        Note: original sentence is ignored. It is only used in the evaluation.
        """

        num_lines = sum(1 for line in open(hyphenated_file))

        with open(hyphenated_file) as hf:
            with open(result_file, 'w') as rf:
                line_counter = 0
                for line in hf:
                    # Print some progress
                    line_counter += 1
                    self.printProgressBar(line_counter, num_lines, length=50)

                    output_sentence = None

                    # The language model takes a whole line as input
                    if model_type == 'langmod':
                        output_sentence = languagemodel.run(line.strip())
                        continue

                    # Split the hyphenated sentence into words
                    input_sentence, __ = line.strip().split("\t")
                    hyphenated = input_sentence.split()  # input
                    output = []

                    # Run the model on all (fake) hyphenated words
                    for i, word in enumerate(hyphenated):
                        if not re.search(r'[\S]+(?:%s[\S]+)+' %
                                         self.hyphen_sym, word):
                            # If the word is not hyphenated, simply append
                            output.append(word)
                        else:
                            if len(word.split(self.hyphen_sym)) > 2:
                                continue
                            if model_type == 'base' or model_type == 'base2':
                                # Baseline outputs words and confidences
                                confidence = self.model.merge_and_lookup(
                                    word.lower())
                                sorted_confidences = sorted(
                                    confidence.items(),
                                    key=lambda x: x[1], reverse=True)
                                # Find the word with the maximum confidence
                                output.append(sorted_confidences[0][0])
                            elif model_type == 'logreg':
                                # Crf linear regression simply outputs a label
                                if self.model.predict_word(word) == '1':
                                    output.append(
                                        word.replace(self.hyphen_sym, '-'))
                                elif self.model.predict_word(word) == '0':
                                    output.append(
                                        word.replace(self.hyphen_sym, ''))
                            output_sentence = ' '.join(output)

                    # Write the resulting sentence to the result file
                    rf.write("%s\t%s\n" % (input_sentence, output_sentence))

    def printProgressBar(self, iteration, total, length=100, fill='█'):
        """
        Call in a loop to create terminal progress bar
        https://stackoverflow.com/questions/3173320/
        text-progress-bar-in-the-console

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
    if len(sys.argv) != 5:
        print("""Usage: python3 process_file.py """
              """<type: 'base', 'base2', 'logreg', 'langmod'> """
              """<vocab or model or pass> <path to hyphenated file> """
              """<path to result file>""")
        sys.exit()

    model_type = sys.argv[1]

    p = ProcessFile(model_type)
    if model_type == 'base':
        vocab = sys.argv[2]
        p.load_basic_baseline(vocab)
    elif model_type == 'base2':
        vocab = sys.argv[2]
        p.load_baseline_with_supplements(vocab)
    elif model_type == 'logreg':
        model_file = sys.argv[2]
        p.load_linear_regression(model_file)
    elif model_type != 'langmod':
        print("Model type not valid")
        sys.exit()

    hyphenated_file = sys.argv[3]
    result_file = sys.argv[4]
    p.run(hyphenated_file, result_file)
