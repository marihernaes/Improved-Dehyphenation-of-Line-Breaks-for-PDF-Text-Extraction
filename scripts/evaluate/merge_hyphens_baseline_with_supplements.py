# Copyright 2019, University of Freiburg,
# Chair of Algorithms and Data Structures.
# Author: Mari Hernaes.

import re


class BaselineWithSupplements:
    """
    Simple baseline algorithm for the "merging hyphenated words" problem.
    Merges the words with hyphens and checks whether the results are valid
    english words. If they are, then merge the words.

    Look the words up in a custom dictionary, made from clueweb.

    If there are two versions of the word in the dictionary, one with a
    hyphen, and one without - merge the word with a confidence score.

    In this version, the dictionary includes words with special characters
    and numbers. For the words with numbers, a special symbol replaces digits
    - for example u03A7, greek capital chi.

    For example: '13-million' is 'XX-million' in the dictionary.
    """

    def __init__(self, word_list_file, hyphen_symbol='\u0387',
                 digit_symbol='\u03A7'):
        """
        Creates a new BaselineWithSupplements
        """
        self.words = {}
        self.hyphen_symbol = hyphen_symbol  # Standard: Greek Ano Teleia
        self.digit_symbol = digit_symbol  # Standard: Greek capital Phi

        with open(word_list_file) as wlf:
            for line in wlf:
                (word, frequency) = line.strip().split('\t')
                self.words[word] = int(frequency)

    def merge_and_lookup(self, custom_hyph_word):
        """
        Merges a custom hyphenated word with and without a normal hyphen, and
        looks up the two versions in the dictionary.

        Return the word with a confidence score, if both versions (with or
        without a hyphen) is found. If only one version is found, return it
        with confidence 1.

        Note: the choice of what to return if the word isn't known at all, is
        an implementation choice. This affects the accuracy of the algorithm.

        Two supplements are added to the regular baseline:

        First special case: words with digits. Replace the digit with the
        custom symbol - the same which is used in the word list - and look up.

        Second special case: if the word has several hyphens, and a part of
        the word can be merged. Try to merge the subword and return this with
        a confidence. For example, for the word 'g1bb3risch-ho rs', recognize
        that 'hours' is a word.

        Returns a dictionary with the word(s) as key(s) and the confidence(s)
        as score(s).

        >>> import os.path
        >>> dir_path = os.path.dirname(os.path.realpath(__file__))
        >>> dir_path = dir_path + '/../examples/'
        >>> word_list = os.path.join(dir_path, 'example_word_list.txt')
        >>> mhb = BaselineWithSupplements(word_list, '$')
        >>> mhb.merge_and_lookup('13-milli$on')  # Word with digits recognized
        {'13-million': 1}
        >>> mhb.merge_and_lookup('ali$ens')  # Plural
        {'aliens': 1}
        >>> d = mhb.merge_and_lookup('e$mail')  # Return with confidence score
        >>> print(sorted(d.items()))
        [('e-mail', 0.43), ('email', 0.57)]
        >>> d = mhb.merge_and_lookup('24$million')  # Digits and conf. score
        >>> print(sorted(d.items()))
        [('24-million', 0.87), ('24million', 0.13)]
        >>> mhb.merge_and_lookup("g1bb3r1sh-hou$rs-a-day")  # Recognize subword
        {'g1bb3r1sh-hours-a-day': 1}
        >>> d = mhb.merge_and_lookup("long$time-g1bb3r1sh")  # Subword confid.
        >>> print(sorted(d.items()))
        [('long-time-g1bb3r1sh', 0.5), ('longtime-g1bb3r1sh', 0.5)]
        >>> mhb.merge_and_lookup("Moth$er-F*^@")  # Sorry, comes from clueweb.
        {'mother-f*^@': 1}
        """

        merged_word = custom_hyph_word.lower().replace(self.hyphen_symbol, '')

        # Normalize the special hyphenation to look up in dictionary
        hyphenated_word = custom_hyph_word.lower().replace(
                                                  self.hyphen_symbol, '-')

        # NORMAL CASE (if the word does not include a number)
        if re.search(r'[0-9]', custom_hyph_word) is None:
            # Look up the merged word
            if merged_word in self.words:
                # If necessary, calculate confidence scores
                if hyphenated_word in self.words:
                    return self.calculate_confidence_score(hyphenated_word,
                                                           merged_word)
                # If not, return the merged word with confidence 1
                return dict.fromkeys([merged_word], 1)
            # If only the hyphenated word is found
            if hyphenated_word in self.words:
                return dict.fromkeys([hyphenated_word], 1)

        # FIRST SPECIAL CASE (if the input word includes a number)
        else:
            # Replace numbers with the special character
            no_digit_merged_word = re.sub(
                r'[0-9]', self.digit_symbol, merged_word)
            no_digit_hyphenated_word = re.sub(
                r'[0-9]', self.digit_symbol, hyphenated_word)
            # Look up the merged word
            if no_digit_merged_word in self.words:
                # If necessary, calculate confidence score
                if no_digit_hyphenated_word in self.words:
                    confidences = self.calculate_confidence_score(
                                    no_digit_hyphenated_word,
                                    no_digit_merged_word)
                    # But return the result with normal numbers
                    result = {}
                    for c in confidences:
                        if re.search(r'-', c):
                            result[hyphenated_word] = confidences[c]
                        else:
                            result[merged_word] = confidences[c]
                    return result
                # If not, return the merged word with confidence 1
                return dict.fromkeys([merged_word], 1)
            # If only the hyphenated word is found
            if no_digit_hyphenated_word in self.words:
                return dict.fromkeys([hyphenated_word], 1)

        # SECOND SPECIAL CASE (if the word has more hyphens, look up a subword)
        if re.search(r'-', custom_hyph_word):
            # Split the word on the custom hyphen symbol
            (left, right) = custom_hyph_word.lower().split(self.hyphen_symbol)
            # Find the last hyphen index in the left part
            left_hyphen_index = left.rfind('-')
            # And the first hyphen index in the right part
            right_hyphen_index = right.find('-') if \
                right.find('-') > 0 else len(right)

            # Extract the target part (e.g. mil$lion in multi-mil$lion-dollar)
            subword_prefix = left[left_hyphen_index + 1:]
            subword_suffix = right[:right_hyphen_index]

            # Look up the subword
            if (subword_prefix + subword_suffix) in self.words:
                # If necessary, calculate confidence score
                if (subword_prefix + '-' + subword_suffix) in self.words:
                    confidences = self.calculate_confidence_score(
                                        subword_prefix + subword_suffix,
                                        subword_prefix + '-' + subword_suffix)
                    # But return the whole word
                    result = {}
                    for c in confidences:
                        if re.search(r'-', c):
                            result[hyphenated_word] = confidences[c]
                        else:
                            result[merged_word] = confidences[c]
                    return result
                # If not, return the merged word with confidence 1
                return dict.fromkeys([merged_word], 1)
            # If only the hyphenated subword was found
            if (subword_prefix + '-' + subword_suffix) in self.words:
                return dict.fromkeys([hyphenated_word], 1)

        # If the word wasn't found at all
        return dict.fromkeys([merged_word], 0)

    def calculate_confidence_score(self, hyphenated_word, merged_word):
        """
        For a hyphenated word and the corresponding merged one, return the
        confidence scores, based on the number of occurences in the dictionary.

        >>> import os.path
        >>> dir_path = os.path.dirname(os.path.realpath(__file__))
        >>> dir_path = dir_path + '/../examples/'
        >>> word_list = os.path.join(dir_path, 'example_word_list.txt')
        >>> mhb = BaselineWithSupplements(word_list)
        >>> d = mhb.calculate_confidence_score('e-mail', 'email')
        >>> print(sorted(d.items()))
        [('e-mail', 0.43), ('email', 0.57)]
        """

        confidences = {}

        # Sum up the frequencies
        merged_freqency = self.words[merged_word]
        hyphenated_frequency = \
            self.words[hyphenated_word] if hyphenated_word in self.words else 0
        total = merged_freqency + hyphenated_frequency

        # Add merged word and the corresponding confidence score
        confidences[merged_word] = round(merged_freqency / total, 2)

        # And the same for the hyphenated word
        confidences[hyphenated_word] = round(hyphenated_frequency / total, 2)

        return confidences
