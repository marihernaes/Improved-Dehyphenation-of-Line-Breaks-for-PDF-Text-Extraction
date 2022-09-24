"""
A script that uses the language model trained by Matthias Hertel in his
master's project (see the blog post for more information about the model:
http://ad-blog.informatik.uni-freiburg.de/post/tokenization-repair-using-
character-based-neural-language-models/) to dehyphenate words.

The script evaluates how accurate the model can predict whether a hyphen in
a hyphenated word is mandatory (even after merging the word parts) or not.
"""

import argparse
import json
import string
import sys
import urllib.parse

import requests

# =============================================================================

# The scheme of the API url, with placeholder '%s' instead of the actual query.
API_URL_SCHEME = "http://vulcano:8900/api?q=%s"

# The character used to represent a hyphenation position in a word.
HYPHENATION_SYMBOL = "·"

# Note that the last three chars are different from each other.
PUNCTUATION_SYMBOLS = string.punctuation + " " + "\xa0" + "–" + "—" + "―"

# =============================================================================


def run(benchmark_file):
    """
    Runs the evaluation on the given benchmark file.
    """

    # In this script, we will extensively use the shorthands
    # "v0" and "v1" in the variable names
    # "v0" means "remove the hyphen".
    # "v1" means "keep the hyphen".

    num_predicted_v0_expected_v0 = 0
    num_predicted_v0_expected_v1 = 0
    num_predicted_v1_expected_v0 = 0
    num_predicted_v1_expected_v1 = 0

    num_predicted_v0_expected_v0_ambiguous = 0
    num_predicted_v1_expected_v1_ambiguous = 0
    num_predicted_v0_expected_v1_ambiguous = 0
    num_predicted_v1_expected_v0_ambiguous = 0

    num_error_category_1 = 0
    num_error_category_2 = 0
    num_error_category_3 = 0
    num_error_category_4 = 0

    # Read the benchmark file line by line.
    with open(benchmark_file, "r", encoding="utf-8") as bf:
        for line_num, line in enumerate(bf):
            sys.stdout.write("%s\r" % line_num)

            input_sentence, expected_sentence = line.strip().split("\t")
            # Remove words of only punctuation symbols from input sentence.
            input_words = []
            for word in input_sentence.strip().split():
                word = word.strip()
                for char in word:
                    if char not in PUNCTUATION_SYMBOLS and word:
                        input_words.append(word)
                        break

            # Remove words of only punctuation symbols from expected sentence.
            expected_words = []
            for word in expected_sentence.strip().split():
                word = word.strip()
                for char in word:
                    if char not in PUNCTUATION_SYMBOLS and word:
                        expected_words.append(word)
                        break

            # Consider two variants (v0 and v1) of the input sentence:
            # v0: The input words with all HYPH_SYMBOL removed.
            # v1: The input words with all HYPH_SYMBOL replaced by "-".

            # The words of the input sentence v0.
            input_words_v0 = []
            # The words of the input sentence v1.
            input_words_v1 = []
            # The boundaries of the words in the input sentence v0.
            word_boundaries_v0 = []
            # The boundaries of the words in the input sentence v1.
            word_boundaries_v1 = []
            # The current character index in the input sentence v0.
            index_v0 = 0
            # The current character index in the input sentence v1.
            index_v1 = 0
            # The positions of the hyphenated words in the input sentence.
            positions_hyphenated_words = []

            # Obtain (1) positions of hyphenated words in the input sentence
            # and (2) word boundaries in both variants of the input sentence.
            for word_pos, word in enumerate(input_words):
                if any([c == HYPHENATION_SYMBOL for c in word]):
                    # The word contains a hyphenation symbol.
                    positions_hyphenated_words.append(word_pos)
                    input_words_v0.append(word.replace(
                                          HYPHENATION_SYMBOL, ""))
                    input_words_v1.append(word.replace(
                                          HYPHENATION_SYMBOL, "-"))
                else:
                    # The word doesn't contain a hyphenation symbol.
                    input_words_v0.append(word)
                    input_words_v1.append(word)

                word_boundaries_v0.append(
                    (index_v0, index_v0 + len(input_words_v0[-1])))
                word_boundaries_v1.append(
                    (index_v1, index_v1 + len(input_words_v1[-1])))
                # + 1 because of the whitespaces between words.
                index_v0 += len(input_words_v0[-1]) + 1
                index_v1 += len(input_words_v1[-1]) + 1

            # Send request to the API using the v0 input sentence.
            input_sentence_v0 = " ".join(input_words_v0)
            url_v0 = API_URL_SCHEME % urllib.parse.quote(input_sentence_v0)
            try:
                res_v0 = requests.get(url_v0)
                json_v0 = json.loads(res_v0.text)
                if (res_v0.status_code != 200 or not res_v0.text):
                    print("WARNING: Could not process sentence #%d." %
                          line_num)
                    print("status code: %s, status message: %s" %
                          (res_v0.status_code, res_v0.text))
                    continue
            except KeyboardInterrupt:
                sys.exit(1)
            except ConnectionError:
                print(
                    "Please restart web server at http://vulcano:8900. "
                    "Use docker container at ad-svn.informatik.uni-freiburg.de"
                    "/student-projects/matthias-hertel")
                sys.exit(1)
            except Exception:
                print("WARNING: Could not process sentence #%d properly." %
                      line_num)
                continue

            # Send request to the API using the v1 input sentence.
            input_sentence_v1 = " ".join(input_words_v1)
            url_v1 = API_URL_SCHEME % urllib.parse.quote(input_sentence_v1)
            try:
                res_v1 = requests.get(url_v1)
                json_v1 = json.loads(res_v1.text)
                if (res_v1.status_code != 200 or not res_v1.text):
                    print("WARNING: Could not process sentence #%d properly." %
                          line_num)
                    print("status code: %s, status message: %s" %
                          (res_v1.status_code, res_v1.text))
                    continue
            except KeyboardInterrupt:
                sys.exit(1)
            except Exception:
                print("WARNING: Could not process sentence #%d." % line_num)
                continue

            # Iterate the hyphenated words. Decide to keep the hyphen or not.
            for word_pos in positions_hyphenated_words:
                # V0: Compute the probability of the word *without* hyphen.
                w_start_v0, w_end_v0 = word_boundaries_v0[word_pos]
                input_word_v0 = input_words_v0[word_pos]
                # Compute probability by summing up characters probabilities.
                prob_word_v0 = 0
                for i_word, i_sent in enumerate(range(w_start_v0, w_end_v0)):
                    prob_word_v0 += json_v0[i_sent].get(
                        input_word_v0[i_word], 0)
                prob_word_v0 /= len(input_word_v0)
                prob_word_v0 = round(prob_word_v0, 2)

                # V1: Compute the probability of the word *with* hyphen.
                w_start_v1, w_end_v1 = word_boundaries_v1[word_pos]
                input_word_v1 = input_words_v1[word_pos]
                # Compute probability by summing up characters probabilities.
                prob_word_v1 = 0
                for i_word, i_sent in enumerate(range(w_start_v1, w_end_v1)):
                    prob_word_v1 += json_v1[i_sent].get(
                        input_word_v1[i_word], 0)
                prob_word_v1 /= len(input_word_v1)
                prob_word_v1 = round(prob_word_v1, 2)

                # Decide: is the prediction correct?
                if prob_word_v1 > 0.5:
                    prediction_keep_hyphen = round(
                        prob_word_v1 - prob_word_v0, 2) > 0.01
                else:
                    prediction_keep_hyphen = round(
                        prob_word_v1 - prob_word_v0, 2) >= 0.1

                if prediction_keep_hyphen:
                    predicted_word = input_word_v1
                    predicted_word_prob = prob_word_v1
                    expected_word_prob = prob_word_v0
                else:
                    predicted_word = input_word_v0
                    predicted_word_prob = prob_word_v0
                    expected_word_prob = prob_word_v1
                expected_word = expected_words[word_pos]

                if predicted_word == expected_word:
                    # Prediction is correct.
                    if prediction_keep_hyphen:
                        num_predicted_v1_expected_v1 += 1
                        num_predicted_v1_expected_v1_ambiguous += 1
                    else:
                        num_predicted_v0_expected_v0 += 1
                        num_predicted_v0_expected_v0_ambiguous += 1
                else:
                    # Prediction is not correct.
                    if prediction_keep_hyphen:
                        num_predicted_v1_expected_v0 += 1
                        if prob_word_v0 >= 0.75 and prob_word_v1 >= 0.75:
                            num_predicted_v0_expected_v0_ambiguous += 1
                        else:
                            num_predicted_v1_expected_v0_ambiguous += 1
                    else:
                        num_predicted_v0_expected_v1 += 1
                        if prob_word_v0 >= 0.75 and prob_word_v1 >= 0.75:
                            num_predicted_v1_expected_v1_ambiguous += 1
                        else:
                            num_predicted_v0_expected_v1_ambiguous += 1
                    print("Wrong prediction.")
                    print("Input sentence:   ", input_sentence)
                    print("Expected sentence:", expected_sentence)
                    print("Predicted word: %s (%.2f)" %
                          (predicted_word, predicted_word_prob))
                    print("Expected word: %s (%.2f)" %
                          (expected_word, expected_word_prob))
                    print("-" * 30)

                    if prob_word_v0 >= 0.5 and prob_word_v1 >= 0.5:
                        num_error_category_1 += 1
                    if prob_word_v0 < 0.5 and prob_word_v1 >= 0.5:
                        num_error_category_2 += 1
                    if prob_word_v0 >= 0.5 and prob_word_v1 < 0.5:
                        num_error_category_3 += 1
                    if prob_word_v0 < 0.5 and prob_word_v1 < 0.5:
                        num_error_category_4 += 1

            if (line_num + 1) % 100 == 0:
                # Output some evaluation results.
                accuracy = (num_predicted_v0_expected_v0 +
                            num_predicted_v1_expected_v1) / (
                            num_predicted_v0_expected_v0 +
                            num_predicted_v0_expected_v1 +
                            num_predicted_v1_expected_v0 +
                            num_predicted_v1_expected_v1)
                accuracy_amb = (num_predicted_v0_expected_v0_ambiguous +
                                num_predicted_v1_expected_v1_ambiguous) / (
                                num_predicted_v0_expected_v0_ambiguous +
                                num_predicted_v0_expected_v1_ambiguous +
                                num_predicted_v1_expected_v0_ambiguous +
                                num_predicted_v1_expected_v1_ambiguous)
                print("Intermediate result", line_num + 1)
                print("Accuracy:                        %.2f%%" %
                      (accuracy * 100))
                print("Accuracy*:                       %.2f%%" %
                      (accuracy_amb * 100))
                print("Accuracy 'expected non-hyphen':  %.2f%%" %
                      (100 * num_predicted_v0_expected_v0 / (
                       num_predicted_v0_expected_v0 +
                       num_predicted_v1_expected_v0)))
                print("Accuracy 'expected non-hyphen'*: %.2f%%" %
                      (100 * num_predicted_v0_expected_v0_ambiguous / (
                       num_predicted_v0_expected_v0_ambiguous +
                       num_predicted_v1_expected_v0_ambiguous)))
                print("Accuracy 'expected hyphen':      %.2f%%" %
                      (100 * num_predicted_v1_expected_v1 / (
                       num_predicted_v0_expected_v1 +
                       num_predicted_v1_expected_v1)))
                print("Accuracy 'expected hyphen'*:     %.2f%%" %
                      (100 * (num_predicted_v1_expected_v1_ambiguous) / (
                       num_predicted_v0_expected_v1_ambiguous +
                       num_predicted_v1_expected_v1_ambiguous)))
                print("")
                print("Confusion Matrix:")
                print("                expected '':   expected '-':")
                print("predicted '' :  %s     %s" %
                      (str(num_predicted_v0_expected_v0).rjust(11),
                       str(num_predicted_v0_expected_v1).rjust(11)))
                print("predicted '-':  %s     %s" %
                      (str(num_predicted_v1_expected_v0).rjust(11),
                       str(num_predicted_v1_expected_v1).rjust(11)))
                print()
                print("Confusion Matrix*:")
                print("                expected '':   expected '-':")
                print("predicted '' :  %s     %s" %
                      (str(num_predicted_v0_expected_v0_ambiguous).rjust(11),
                       str(num_predicted_v0_expected_v1_ambiguous).rjust(11)))
                print("predicted '-':  %s     %s" %
                      (str(num_predicted_v1_expected_v0_ambiguous).rjust(11),
                       str(num_predicted_v1_expected_v1_ambiguous).rjust(11)))
                print("#error category 1:", num_error_category_1)
                print("#error category 2:", num_error_category_2)
                print("#error category 3:", num_error_category_3)
                print("#error category 4:", num_error_category_4)
                print("-" * 30)
        # Output some evaluation results.
        accuracy = (num_predicted_v0_expected_v0 +
                    num_predicted_v1_expected_v1) / (
                    num_predicted_v0_expected_v0 +
                    num_predicted_v0_expected_v1 +
                    num_predicted_v1_expected_v0 +
                    num_predicted_v1_expected_v1)
        accuracy_amb = (num_predicted_v0_expected_v0_ambiguous +
                        num_predicted_v1_expected_v1_ambiguous) / (
                        num_predicted_v0_expected_v0_ambiguous +
                        num_predicted_v0_expected_v1_ambiguous +
                        num_predicted_v1_expected_v0_ambiguous +
                        num_predicted_v1_expected_v1_ambiguous)
        print("Accuracy:                       %.2f%%" % (accuracy * 100))
        print("Accuracy*:                       %.2f%%" % (accuracy_amb * 100))
        print("Accuracy 'expected non-hyphen': %.2f%%" % (
            100 * num_predicted_v0_expected_v0 / (
               num_predicted_v0_expected_v0 +
               num_predicted_v1_expected_v0)))
        print("Accuracy 'expected non-hyphen'*: %.2f%%" % (
            100 * num_predicted_v0_expected_v0_ambiguous / (
               num_predicted_v0_expected_v0_ambiguous +
               num_predicted_v1_expected_v0_ambiguous)))
        print("Accuracy 'expected hyphen':     %.2f%%" %
              (100 * num_predicted_v1_expected_v1 / (
               num_predicted_v0_expected_v1 +
               num_predicted_v1_expected_v1)))
        print("Accuracy 'expected hyphen'*:     %.2f%%" %
              (100 * (num_predicted_v1_expected_v1_ambiguous) / (
               num_predicted_v0_expected_v1_ambiguous +
               num_predicted_v1_expected_v1_ambiguous)))
        print("")
        print("Confusion Matrix:")
        print("                expected '':   expected '-':")
        print("predicted '' :  %s     %s" %
              (str(num_predicted_v0_expected_v0).rjust(11),
               str(num_predicted_v0_expected_v1).rjust(11)))
        print("predicted '-':  %s     %s" %
              (str(num_predicted_v1_expected_v0).rjust(11),
               str(num_predicted_v1_expected_v1).rjust(11)))
        print()
        print("Confusion Matrix*:")
        print("                expected '':   expected '-':")
        print("predicted '' :  %s     %s" %
              (str(num_predicted_v0_expected_v0_ambiguous).rjust(11),
               str(num_predicted_v0_expected_v1_ambiguous).rjust(11)))
        print("predicted '-':  %s     %s" %
              (str(num_predicted_v1_expected_v0_ambiguous).rjust(11),
               str(num_predicted_v1_expected_v1_ambiguous).rjust(11)))
        print("#error category 1:", num_error_category_1)
        print("#error category 2:", num_error_category_2)
        print("#error category 3:", num_error_category_3)
        print("#error category 4:", num_error_category_4)


# =================================================================================================

if __name__ == "__main__":
    # Create a command line argument parser.
    arg_parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # The path to the dataset to use.
    arg_parser.add_argument(
        "--benchmark_file",
        help="The path to a benchmark file that contains lines in the format \
<input_sentence>TAB<expected_sentence>, where <input_sentence> is a single \
sentence containing hyphenated words and <expected_sentence> is the same \
sentence, but the hyphenated words correctly dehyphenated."
    )

    args = arg_parser.parse_args()

    run(args.benchmark_file)
