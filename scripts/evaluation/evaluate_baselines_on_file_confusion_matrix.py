# Copyright 2019, University of Freiburg,
# Chair of Algorithms and Data Structures.
# Author: Mari Hernaes.

import merge_hyphens_baseline
import merge_hyphens_baseline_with_supplements as mhbsuppl
import re
import sys
import time


class EvaluateBaseline:
    """
    ALSO WRITES THE EVALUATION RESULTS TO A CONFUSION MATRIX TO MATCH THE
    OTHER MACHINE LEARNING EVALUATUONS

    Thoroughly evaluates the merging-hyphenated-words baseline algorithm.
    Runs the baseline algorithm on (fake) hyphenated words and compares the
    outputs to the original words.

    Writes a summary of the performance to a text document, and logs fails and
    details to another text document.
    """

    def __init__(self, hyphen_symbol='\u0387'):
        """
        Initializes an evaluate-baseline object.

        Creates four dictionaries, in a confusion matrix style (true positive,
        true negative, false positive, false negative). The word 'positive'
        is referring to 'it is predicted, that the hyphen should stay'.

        A true positive is the cases where a hyphen is kept, and it is correct.
        A true negative is the when the hyphen is merged, and it is correct.
        """
        self.hyphen = hyphen_symbol  # Standard: Greek Ano Teleia
        self.mhb = None
        self.tp = {}  # True positive
        self.tp_counter = 0
        self.tn = {}  # True negative
        self.tn_counter = 0
        self.fn = {}  # False negative
        self.fn_counter = 0
        self.fp = {}  # False positive
        self.fp_counter = 0

    def load_basic_baseline(self, word_list):
        """ Prepares the baseline by loading the dictionary."""

        self.mhb = merge_hyphens_baseline.MergeHyphensBaseline(word_list,
                                                               self.hyphen)

    def load_baseline_with_supplements(self, word_list):
        """ Prepares the baseline by loading the dictionary."""

        self.mhb = mhbsuppl.BaselineWithSupplements(word_list,
                                                    self.hyphen)

    def evaluate_baseline_on_file(self, hyphenated_file):
        """
        Evaluates the baseline on a (fake) hyphenated file. The file should be
        in the format <hyphenated sentence> TAB <original sentence>.

        Split the two sentences into lists of words, and run the baseline
        algorithm on all (fake) hyphenated words. Compare each output word
        to the original word on the same index.
        """
        num_lines = sum(1 for line in open(hyphenated_file))

        with open(hyphenated_file) as hf:
            line_counter = 0
            for line in hf:
                # Print some progress
                line_counter += 1
                self.printProgressBar(line_counter, num_lines, length=50)

                line = line.split("\t")
                # Split the sentences into words
                hyphenated = line[0].strip().split()  # input
                original = line[1].strip().split()  # expected output
                # The two sentences should be the same length
                if len(hyphenated) != len(original):
                    import pdb
                    pdb.set_trace()

                # Run the baseline on all (fake) hyphenated words
                for i, h in enumerate(hyphenated):
                    input = h.lower()
                    if re.search(r'[\S]+(?:%s[\S]+)+' % self.hyphen, input):
                        baseline_confidence = self.mhb.merge_and_lookup(input)
                        # The baseline outputs a dict of words and confidences
                        sorted_confidences = sorted(
                            baseline_confidence.items(),
                            key=lambda x: x[1], reverse=True)
                        # Find the word with the maximum confidence
                        output = sorted_confidences[0][0]
                        output_confidence = sorted_confidences[0][1]

                        # Compare to expected output (normalized) on same index
                        exp_outputput = original[i].lower()
                        self.evaluate_words(input, output, exp_outputput,
                                            output_confidence)

                # Print progress for each 2.500.000 line
                if (line_counter % 2500000) == 0:
                    print("...%d sentences processed..." % line_counter)

    def evaluate_words(self, input, output, exp_outputput, confidence):
        """
        Compare a (fake) hyphenated word to the expected output.

        Append the result to the correct dictionary (TP, TN, FN or FP), in
        the following style: 'raw word':  {'frequency': 0, confidence': int}.
        If this excact mistake already exists, increment the frequency.

        At the same time, increment the total counter for this type of result.

        >>> eb = EvaluateBaseline('*')

        >>> eb.evaluate_words('e*mail', 'e-mail', 'email', 0.8)  # FP
        >>> sorted(eb.fp['e*mail'].items())
        [('confidence', 0.8), ('frequency', 1)]

        >>> eb.evaluate_words('long*term', 'longterm', 'long-term', 0.51)  # FN
        >>> sorted(eb.fn['long*term'].items())
        [('confidence', 0.51), ('frequency', 1)]

        >>> eb.evaluate_words('low*scale', 'low-scale', 'low-scale', 0.9)  # TP
        >>> sorted(eb.tp['low*scale'].items())
        [('confidence', 0.9), ('frequency', 1)]

        >>> eb.evaluate_words('wo*rd', 'word', 'word', 1)  # TN
        >>> sorted(eb.tn['wo*rd'].items())
        [('confidence', 1), ('frequency', 1)]

        >>> eb.evaluate_words('e*mail', 'e-mail', 'email', 0.8)  # FP again
        >>> sorted(eb.fp['e*mail'].items())
        [('confidence', 0.8), ('frequency', 2)]
        >>> eb.fp_counter
        2
        """

        # If the output and expected output are identical
        if exp_outputput == output:
            # The original word has a hyphen in same position
            if exp_outputput == input.replace(self.hyphen, '-'):
                # TRUE POSITIVE
                self.tp_counter += 1
                if input not in self.tp:
                    self.tp[input] = {'frequency': 1, 'confidence': confidence}
                else:
                    self.tp[input]['frequency'] += 1
            else:
                # TRUE NEGATIVE
                self.tn_counter += 1
                if input not in self.tn:
                    self.tn[input] = {'frequency': 1, 'confidence': confidence}
                else:
                    self.tn[input]['frequency'] += 1
        else:  # If the output and expected output are different
            # The original word has a hyphen in same position
            if exp_outputput == input.replace(self.hyphen, '-'):
                # FALSE NEGATIVE
                self.fn_counter += 1
                if input not in self.fn:
                    self.fn[input] = {'frequency': 1, 'confidence': confidence}
                else:
                    self.fn[input]['frequency'] += 1
            else:
                # FALSE POSITIVE
                self.fp_counter += 1
                if input not in self.fp:
                    self.fp[input] = {'frequency': 1, 'confidence': confidence}
                else:
                    self.fp[input]['frequency'] += 1

    def report_overall_result(self, k=5):
        """ Renders the result to be easily readable. Returns a string."""
        reports = []
        total_counter = self.tp_counter + self.tn_counter \
            + self.fp_counter + self.fn_counter

        # True positive cases (predicted: hyphen  expected: hyphen)
        reports.extend(self.render_case(
            'TP', total_counter, self.tp, self.tp_counter))
        # True negative cases (predicted: merge   expected: merge)
        reports.append(self.render_case(
            'TN', total_counter, self.tn, self.tn_counter)[1])
        # False positive cases (predicted: hyphen expected: merge)
        reports.append(self.render_case(
            'FP', total_counter, self.fp, self.fp_counter)[1])
        # False negative cases (predicted: merge  expected: hyphen)
        reports.append(self.render_case(
            'FN', total_counter, self.fn, self.fn_counter)[1])

        # Top k frequent word for each case
        top_frequent_words = '\n\n{}\n{}{}\n\n{}{}\n\n{}{}\n\n{}{}\n'.format(
                'Top %d frequent words for the different cases:\n' % k,
                'True positive cases (predicted hyphen, expected hyphen):\n',
                self.render_examples(self.frequency_sort(self.tp)[:k]),
                'True negative cases (predicted merge, expected merge):\n',
                self.render_examples(self.frequency_sort(self.tn)[:k]),
                'False positive cases (predicted hyphen, expected merge):\n',
                self.render_examples(self.frequency_sort(self.fp)[:k]),
                'False negative cases (predicted merge, expected hyphen):\n',
                self.render_examples(self.frequency_sort(self.fn)[:k])
        )

        return '\n'.join(reports) + top_frequent_words

    def render_case(self, case, total_counter, case_dict, case_counter):
        """
        Report the result from one of the case dictionaries, in a way which
        is easily readable.

        >>> eb = EvaluateBaseline('*')
        >>> eb.evaluate_words('e*mail', 'e-mail', 'email', 0.8)  # FP
        >>> eb.evaluate_words('e*mail', 'e-mail', 'email', 0.8)  # FP again
        >>> (header, info) = eb.render_case('X', 5, eb.fp, eb.fp_counter)
        >>> expec = '{:<19}{:<19}{:<19}{:<19}'.format('X', '1','2','40.000%')
        >>> expec += '{:<19}{:<19}{:<19}{:<19}'.format('0', '0','1','0.800')
        >>> info == expec
        True
        """
        # Prepare to report the different confidences
        confidence_one = 0
        confidence_zero = 0
        ambiguous_confidences = {}
        for key, value in case_dict.items():
            if value['confidence'] == 1:
                confidence_one += 1
            elif value['confidence'] == 0:
                confidence_zero += 1
            elif value['confidence'] in ambiguous_confidences:
                ambiguous_confidences[value['confidence']] += 1
            else:
                ambiguous_confidences[value['confidence']] = 1

        # Confidence for the amgigous cases (multiplied by freqency)
        ambiguous_sum = 0
        ambiguous_total_frequency = 0
        for score, frequency in ambiguous_confidences.items():
            ambiguous_sum += (score * frequency)
            ambiguous_total_frequency += frequency
        avg_confidence = (ambiguous_sum / ambiguous_total_frequency) if \
            ambiguous_total_frequency > 0 else ambiguous_sum

        avg_confidence_string = '{:.3f}'.format(avg_confidence)
        ratio_of_total_string = '{:.3f}%'.format(
            ((case_counter / total_counter) * 100))

        header = '{:<19}{:<19}{:<19}{:<19}{:<19}{:<19}{:<19}{:<19}'.format(
            'Case type',
            'Unique words',
            'Case counter',
            'Ratio of total',
            'Confidence one',
            'Confidence zero',
            'Ambiguous cases',
            'Average ambiguous confidence'
        )
        info = '{:<19}{:<19}{:<19}{:<19}{:<19}{:<19}{:<19}{:<19}'.format(
            case,
            len(case_dict),
            case_counter,
            ratio_of_total_string,
            confidence_one,
            confidence_zero,
            ambiguous_total_frequency,
            avg_confidence_string
        )

        return [header, info]

    def report_mistake_results(self, false_case_dict, false_case_counter, k=9):
        """ For a false case, explain its mistakes. Returns a string"""

        # Put mistakes in different categories
        spelling_mistake_in_data = {}  # High confidence, but marked failed
        word_not_in_dictionary = {}  # Confidence zero
        several_valid_spellings = {}

        for (mistake, details) in false_case_dict.items():
            if details['confidence'] > 0.9:
                spelling_mistake_in_data[mistake] = details
            elif details['confidence'] == 0:
                word_not_in_dictionary[mistake] = details
            else:
                several_valid_spellings[mistake] = details

        # Render an output of all mistakes
        output = ['Mistakes in total: %d (%d unique). Categories:' % (
            false_case_counter, len(false_case_dict))]

        output.append('Showing top %s of each category' % k)

        if spelling_mistake_in_data:
            top_k_sm = self.frequency_sort(spelling_mistake_in_data)[:k]
            output.append('Spelling mistake in data set (%d)\n' % len(
                spelling_mistake_in_data)
                + self.render_examples(top_k_sm))
        if word_not_in_dictionary:
            top_k_wnd = self.frequency_sort(word_not_in_dictionary)[:k]
            output.append('Word not in dictionary (%d)\n' % len(
                word_not_in_dictionary)
                + self.render_examples(top_k_wnd))
        if several_valid_spellings:
            top_k_svs = self.frequency_sort(several_valid_spellings)[:k]
            output.append('Several valid spellings (%d)\n' % len(
                several_valid_spellings)
                + self.render_examples(top_k_svs))

        return '\n\n'.join(output)

    def render_examples(self, case_list):
        """ Renders examples of words and details to be easily readable. """
        # Header
        output = ['{:<30}{:<20}{:<5}'.format(
            'frequency', 'mistake', 'confidence score')]

        # Words and details
        for (word, info) in case_list:
            output.append('{:<30}{:<20}{:<5}'.format(
                info['frequency'], word, info['confidence']))

        return '\n'.join(output)

    def frequency_sort(self, case_dict):
        """ Sort a case dictonary by the frequencies. Return as a list """
        return sorted(
            case_dict.items(), key=lambda x: x[1]['frequency'], reverse=True)

    def evaluate_accuracy(self):
        # Initialize counters for confusion matrix.
        # d: delete the hyphen; k: keep the hyphen.
        # For example: num_d_d = number_predicted_delete_expected_delete
        num_d_d = self.tn_counter
        num_d_k = self.fn_counter
        num_k_d = self.fp_counter
        num_k_k = self.tp_counter

        accuracy = (num_d_d + num_k_k) / (
                    num_d_d + num_d_k + num_k_d + num_k_k)

        # Create the evaluation values
        evl = []
        evl.append("Accuracy:                       %.2f%%" % (accuracy * 100))
        evl.append("Accuracy 'expected non-hyphen': %.2f%%" % (
            100 * num_d_d / (num_d_d + num_k_d)))
        evl.append("Accuracy 'expected hyphen':     %.2f%%" % (
            100 * num_k_k / (num_d_k + num_k_k)))
        evl.append("")
        evl.append("Confusion Matrix:")
        evl.append("                expected '':   expected '-':")
        evl.append("predicted '' :  %s     %s" % (
            str(num_d_d).rjust(11), str(num_d_k).rjust(11)))
        evl.append("predicted '-':  %s     %s" % (
            str(num_k_d).rjust(11), str(num_k_k).rjust(11)))
        result_string = '\n'.join(evl)

        return result_string

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
    if len(sys.argv) != 5:
        print("""Usage: python3 evaluate_baseline.py <version 1 or 2>"""
              """ <path to hyphenated file> <custom word list.txt>"""
              """ <filename for .._faillog.txt / .._results.txt / """
              """.._confusion-matrix.txt>""")
        sys.exit()

    baseline_version = sys.argv[1]
    hyphenated_file = sys.argv[2]
    word_list = sys.argv[3]
    fail_filename = sys.argv[4] + '_faillog.txt'
    summary_filename = sys.argv[4] + '_results.txt'
    confusion_matrix_filename = sys.argv[4] + '_confusion-matrix.txt'

    # Initialize
    start = time.time()
    sys.stdout.write("Loading the custom word list: %.s\n" % word_list)
    eb = EvaluateBaseline()

    # Load the given baseline version
    if int(baseline_version) == 1:
        eb.load_basic_baseline(word_list)
    elif int(baseline_version) == 2:
        eb.load_baseline_with_supplements(word_list)
    else:
        print("Version number must be 1 (basic baseline) or 2 (supplemented)")
        sys.exit()

    version_string = "Baseline version: %s\n\n" % (
                'basic' if int(baseline_version) == 1 else 'supplemented')

    stop = time.time()
    sys.stdout.write("Done. (%.4f)\n%s\n" % ((stop - start), version_string))

    hyphenated_files = [hyphenated_file]

    # Process the files
    total_start = time.time()
    for hf in hyphenated_files:
        start = time.time()
        sys.stdout.write("Evaluating baseline on: %s\n" % hf)
        eb.evaluate_baseline_on_file(hf)
        stop = time.time()
        sys.stdout.write("Done. (%.4f)\n" % (stop - start))

        # TOP K FOR EACH CATEGORY TP, TN, FP, FN
        summary = eb.report_overall_result(10)
        sys.stdout.write("Confusion matrix:\n%s\n" %
                         version_string + '\n' + eb.evaluate_accuracy())

        with open(summary_filename, 'w') as sf:
            sf.write(version_string)
            sf.write(summary)
            sys.stdout.write('Intermediate summary written to file.\n')

        with open(fail_filename, 'w') as ff:
            ff.write(version_string)
            ff.write('FALSE POSITIVES\n(hyphen should have been merged)\n')
            # TOP K FOR EACH MISTAKE CATEGORY FOR FALSE POSITIVES
            ff.write(eb.report_mistake_results(eb.fp, eb.fp_counter, 42))
            ff.write('\n\n::::::::::::::::::::::::::::::::::::::::\n\n')
            ff.write('FALSE NEGATIVES\n(hyphen should have been kept)\n')
            # TOP K FOR EACH MISTAKE CATEGORY FOR FALSE NEGATIVES
            ff.write(eb.report_mistake_results(eb.fn, eb.fn_counter, 42))

        with open(confusion_matrix_filename, 'w') as cf:
            cf.write(version_string)
            cf.write(eb.evaluate_accuracy())

    total_stop = time.time()
    sys.stdout.write("All done. (%.4f)\n" % (total_stop - total_start))
