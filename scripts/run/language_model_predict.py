"""
A script that uses the language model trained by Matthias Hertel in his
master's project (see the blog post for more information about the model:
http://ad-blog.informatik.uni-freiburg.de/post/tokenization-repair-using-
character-based-neural-language-models/) to dehyphenate words. The script
evaluates how accurate the model can predict whether a hyphen in a hyphenated
word is mandatory (even after merging the word parts) or not.
"""

import json
import string
import sys
import urllib.parse
import requests
from requests.exceptions import ConnectionError


# ============================================================================

# The scheme of the API url, with placeholder '%s' instead of the actual query.
API_URL_SCHEME = "http://vulcano:8900/api?q=%s"

# The character used to represent a hyphenation position in a word.
HYPHENATION_SYMBOL = "·"

# Note that the last three chars are different from each other.
PUNCTUATION_SYMBOLS = string.punctuation + " " + "\xa0" + "–" + "—" + "―"

# ============================================================================


def run(sentence):
    """
    Runs the script on a given hyphenated sentence.
    """

    # Make a list of input words
    input_words = []
    for word in sentence.split():
        word = word.strip()
        for char in word:
            if char not in PUNCTUATION_SYMBOLS and word:
                input_words.append(word)
                break

    # Consider two variants (v0 and v1) of the input sentence:
    # v0: The input words with all occurences of HYPH_SYMBOL removed.
    # v1: The input words with all occurences of HYPH_SYMBOL replaced by "-".

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

    # Obtain (1) the positions of the hyphenated words in the input sentence
    # and (2) the word boundaries in both variants of the input sentence.
    for word_pos, word in enumerate(input_words):
        if any([c == HYPHENATION_SYMBOL for c in word]):
            # The word contains a hyphenation symbol.
            positions_hyphenated_words.append(word_pos)
            input_words_v0.append(word.replace(HYPHENATION_SYMBOL, ""))
            input_words_v1.append(word.replace(HYPHENATION_SYMBOL, "-"))
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
            print("WARNING: Couldn't process sentence properly.")
            print("status code: %s, status message: %s" %
                  (res_v0.status_code, res_v0.text))
    except KeyboardInterrupt:
        sys.exit(1)
    except ConnectionError:
        print(
            "Please restart web server at http://vulcano:8900. "
            "Use docker container at ad-svn.informatik.uni-freiburg.de/"
            "student-projects/matthias-hertel")
        sys.exit(1)
    except Exception:
        print("WARNING: Couldn't process sentence properly.")

    # Send request to the API using the v1 input sentence.
    input_sentence_v1 = " ".join(input_words_v1)
    url_v1 = API_URL_SCHEME % urllib.parse.quote(input_sentence_v1)
    try:
        res_v1 = requests.get(url_v1)
        json_v1 = json.loads(res_v1.text)
        if (res_v1.status_code != 200 or not res_v1.text):
            print("WARNING: Couldn't process sentence properly")
            print("status code: %s, status message: %s" %
                  (res_v1.status_code, res_v1.text))
    except KeyboardInterrupt:
        sys.exit(1)
    except ConnectionError:
        print(
            "Please restart web server at http://vulcano:8900."
            "Use docker container at ad-svn.informatik.uni-freiburg.de/"
            "student-projects/matthias-hertel")
        sys.exit(1)
    except Exception:
        print("WARNING: Couldn't process sentence properly.")

    # Iterate the hyphenated words. Decide whether to keep the hyphen or not.
    dehyphenated_words = []
    for word_pos in positions_hyphenated_words:
        # V0: Compute the probability of the word *without* hyphen.
        word_start_v0, word_end_v0 = word_boundaries_v0[word_pos]
        input_word_v0 = input_words_v0[word_pos]
        # Compute the probability by summing up the characters probabilities.
        prob_word_v0 = 0
        for i_word, i_sentence in enumerate(range(word_start_v0, word_end_v0)):
            prob_word_v0 += json_v0[i_sentence].get(input_word_v0[i_word], 0)
        prob_word_v0 /= len(input_word_v0)
        prob_word_v0 = round(prob_word_v0, 2)

        # V1: Compute the probability of the word *with* hyphen.
        word_start_v1, word_end_v1 = word_boundaries_v1[word_pos]
        input_word_v1 = input_words_v1[word_pos]
        # Compute the probability by summing up the characters probabilities.
        prob_word_v1 = 0
        for i_word, i_sentence in enumerate(range(word_start_v1, word_end_v1)):
            prob_word_v1 += json_v1[i_sentence].get(input_word_v1[i_word], 0)
        prob_word_v1 /= len(input_word_v1)
        prob_word_v1 = round(prob_word_v1, 2)

        # Decide: is the prediction correct?
        if prob_word_v1 > 0.5:
            prediction_keep_hyphen = round(
                prob_word_v1 - prob_word_v0, 2) > 0.01
        else:
            prediction_keep_hyphen = round(
                prob_word_v1 - prob_word_v0, 2) >= 0.1

        # Remember the correct prediction
        if prediction_keep_hyphen:
            dehyphenated_words.append(input_word_v1)
        else:
            dehyphenated_words.append(input_word_v0)

    # Compose the output sentence
    if not positions_hyphenated_words:
        return ' '.join(input_words)

    output_sentence = []
    if len(dehyphenated_words) != len(positions_hyphenated_words):
        print('Error: dehyphenated words and position mismatch')

    i = 0  # Pointer for the dehyphenated words
    j = 0  # Pointer for the hyphenated positions
    for word_pos, word in enumerate(input_words):
        if word_pos == positions_hyphenated_words[j]:
            output_sentence.append(dehyphenated_words[i])
            i += 1
            if (j + 1) < len(positions_hyphenated_words):
                j += 1
        else:
            output_sentence.append(word)

    return ' '.join(output_sentence)


if __name__ == "__main__":
    print(run('t·es·t a sente·nce . % =  sente·nce COMpl*IcA·ted'))
