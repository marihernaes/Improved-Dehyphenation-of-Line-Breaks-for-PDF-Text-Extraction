# Copyright 2019, University of Freiburg,
# Chair of Algorithms and Data Structures.
# Author: Mari Hernaes.

import random
from resources import hyphenate
import re


class HyphenateSentence:
    """ Adds hyphens to a sentence, using Frank Liang's hyphen algorithm. """

    def __init__(self, hyphen_distance=13, hyphen_symbol='\u0387'):
        """
        Constructor. A parameter hyphen_distance defines the approximate
        distance (in words) between each hyphen.
        """
        self.hyphen_distance = hyphen_distance
        self.hyphen_symbol = hyphen_symbol  # Standard: Greek Ano Telia

    def hyphenate_sentence(self, input_sentence):
        """
        Randomly adds hyphens to a (normalized and cleaned) sentence.

        Starts somewhere in the first half of the sentence. If the word on the
        index can't be hyphenated, move on to the next word. If the word can
        be hyphenated, the parameter hyphen_distance defines the distance to
        which the pointer should be moved, allowing several hyphens to be
        inserted in the sentence.

        Returns the sentence, with randomly inserted hyphens (if possible).

        >>> hc = HyphenateSentence()  # Start in the first half
        >>> hc.hyphenate_sentence("A Macbook Macbook")
        'A Mac·book Macbook'
        >>> hc.hyphen_distance = 1  # Hyphenate every word in the sentence
        >>> hc.hyphenate_sentence("A sentence sentence")
        'A sen·tence sen·tence'
        """

        tokens = input_sentence.split(' ')
        n = len(tokens)

        # Random is good - add some randomness to the hyphen parameter
        slack_hyphen_distance = self.hyphen_distance
        if slack_hyphen_distance > 3:
            random_slack = random.randint(-3, 2)
            slack_hyphen_distance += random_slack

        # Start at a random point in the first half of the sentence
        random_index = random.randint(0, (n - 1) // 2)
        pointer = random_index

        while pointer < n:
            # Try to hyphenate
            h = self.hyphenate_token(tokens[pointer])

            # If unsuccessful, try again, word by word, until end
            while not h:
                pointer += 1
                if not pointer < n:  # TODO change?
                    break
                h = self.hyphenate_token(tokens[pointer])

            # If no hyphenation possible
            if not h:
                return ' '.join(tokens)

            # If several hyphenations, choose one randomly
            if len(h) > 2:
                r = random.randint(1, len(h) - 1)

                # Two cases: either the original word has hyphen(s), or not
                original_word = tokens[pointer]
                if re.search(r'-', original_word):
                    # For example 'self-development' has the hyphenation
                    # possibilities ['self', 'de', 'velopment']. For r = 2,
                    # make a pattern 'de-?velopment' and replace this with
                    # 'de·velopment' in self-development
                    try:
                        hyphenated_word = \
                            re.sub('-?'.join([h[r - 1], h[r]]),
                                   self.hyphen_symbol.join([h[r - 1], h[r]]),
                                   original_word, 1)
                    except Exception:
                        print('Joining of hyphenated word failed.')
                else:
                    # For example for 'family' with hyphenations 'fam, il, y'
                    # for r = 2, join '' for [fam, il·y]
                    hyphenated_word = ''.join(self.hyphen_symbol.join(
                                              [''.join(h[:r]),
                                               ''.join(h[r:])]))
            else:
                # If only one hyphenation
                hyphenated_word = self.hyphen_symbol.join(h)

            # Insert hyphenated word in this place in the sentence
            tokens[pointer] = hyphenated_word

            # Increase the pointer to look for more hyphens
            pointer += slack_hyphen_distance

        return ' '.join(tokens)

    def hyphenate_token(self, token):
        """
        Uses Ned's implementation of Frank Liang's algorithm to add a hyphen
        correctly in a word, depending on the syllables.

        For words which originally have a hyphen (UTF-8, 4-STAR), run Ned's
        algorithm on both parts of the word. If UTF-8 has a syllable pattern
        which allows the hyphenation "UT-F-8", but "UTF" can't be hyphenated
        alone, then overwrite the choice of the algorithm and say that "UTF-8"
        is the only valid hyphenation. (Hyphenation patterns are based on
        syllables, and therefore makes unnatural choices for abbreviations).

        Ignore words with ".", "_", "@", "?", (e.g. anything else than letters,
        numbers, apostrophes, diacritics and hyphens).

        Returns an array of the parts which can be hyphenated, if it is
        possible to hyphenate. If not, return false.

        >>> h = HyphenateSentence()
        >>> h.hyphenate_token("sentence")
        ['sen', 'tence']
        >>> h.hyphenate_token("e-mail")  # Fake hyphen on real hyphen
        ['e', 'mail']
        >>> h.hyphenate_token("19th-century")  # Multiple hyphenations
        ['19th', 'cen', 'tu', 'ry']
        >>> h.hyphenate_token("3-star")  # Should not be 3-s-tar
        ['3', 'star']
        >>> h.hyphenate_token("UTF-8")  # Should not be UT-F-8
        False
        >>> h.hyphenate_token("translation_728x90")  # Ignore underscore words
        False
        >>> h.hyphenate_token("cdr")  # Ignore abbreviations
        False
        >>> h.hyphenate_token("sept.")
        False
        >>> h.hyphenate_token("&ampl")
        False
        """

        # Ignore abbreviations and short words
        if len(re.findall(r'[a-zA-Z]', token)) < 4:
            return False

        # Ignore words with latin control characters
        if re.search(r'(\.|\,|@|\&|#|\*|\+|\?|\!|\)|\(|_|\\|<|>)+', token):
            return False

        # For words which already has a hyphen, take special care
        if re.search(r'-', token):
            token = token.split('-')
            parts = []
            for t in token:
                parts.extend(hyphenate.hyphenate_word(t))
            return parts

        # Otherwise, return the hyphenation patterns, or false if not possible
        return False if len(hyphenate.hyphenate_word(token)) == 1 else \
                        hyphenate.hyphenate_word(token)
