# Copyright 2019, University of Freiburg,
# Chair of Algorithms and Data Structures.
# Author: Mari Hernaes.


class MergeHyphensBaseline:
    """
    Simple baseline algorithm for the "merging hyphenated words" problem.
    Merges the words with hyphens and checks whether the results are valid
    english words. If they are, then merge the words.

    Look the words up in a custom dictionary, made from clueweb.

    If there are two versions of the word in the dictionary, one with a
    hyphen, and one without - merge the word with a confidence score.
    """

    def __init__(self, word_list_file, hyphen_symbol='\u0387'):
        """
        Creates a new MergeHyphensBaseline
        """
        self.words = {}
        self.hyphen_symbol = hyphen_symbol  # Standard: Greek Ano Teleia

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

        Note: words with digits (e.g. 1.3-megapixel) are not found in the word
        list and the algorithm fails.

        Returns a dictionary with the word(s) as key(s) and the confidence(s)
        as score(s).

        >>> import os.path
        >>> dir_path = os.path.dirname(os.path.realpath(__file__))
        >>> dir_path = dir_path + '/../examples/'
        >>> word_list = os.path.join(dir_path, 'example_word_list.txt')
        >>> mhb = MergeHyphensBaseline(word_list, '$')
        >>> mhb.merge_and_lookup('ali$ens')  # Plurals should be in dictionary
        {'aliens': 1}
        >>> mhb.merge_and_lookup("african-ameri$can")  # Multiple hyphens work
        {'african-american': 1}
        >>> mhb.merge_and_lookup("Moth$er-F*^@")  # Sorry, comes from clueweb.
        {'mother-f*^@': 0}
        >>> d = mhb.merge_and_lookup('e$mail')  # Return with confidence score
        >>> print(sorted(d.items()))
        [('e-mail', 0.43), ('email', 0.57)]
        """

        merged_word = custom_hyph_word.lower().replace(self.hyphen_symbol, '')

        # Normalize the special hyphenation to look up in dictionary
        hyphenated_word = custom_hyph_word.lower().replace(
                                                  self.hyphen_symbol, '-')

        # Look up the merged word
        if merged_word in self.words:
            # If necessary, calculate confidence score
            if hyphenated_word in self.words:
                return self.calculate_confidence_score(hyphenated_word,
                                                       merged_word)
            # If not, return the word with confidence 1
            return dict.fromkeys([merged_word], 1)

        # If only the hyphenated word is found
        if hyphenated_word in self.words:
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
        >>> mhb = MergeHyphensBaseline(word_list)
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
