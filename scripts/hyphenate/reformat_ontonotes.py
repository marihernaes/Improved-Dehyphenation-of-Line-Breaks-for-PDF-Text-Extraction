# Copyright 2019, University of Freiburg,
# Chair of Algorithms and Data Structures.
# Author: Mari Hernaes.


class ReformatOntonotes:
    """
    A class to read lines from the Ontonotes dataset. One sentence in this
    dataset is in the format <sentence> TAB <postags>.
    """

    def read_line(self, line):
        r"""
        Reads a line from the ontonotes data set and returns a normal sentence,
        e.g. without of POS tags and such.

        Use the pos tags to distinguish between ' - ' as a hyphen, and ' - ' as
        a dash. If it is a hyphen, remove the spaces.

        Replace '-LRB-' and '-RRB-' (left and right hand brackets) in the raw
        text with the proper symbols '(' and ')'.

        >>> r = ReformatOntonotes()
        >>> r.read_line("A super test\tDT JJ NN")
        'A super test'
        >>> r.read_line("A small - scale test\tDT JJ HYPH NN NN")
        'A small-scale test'
        >>> r.read_line("two - year - old\tCD HYPH NN HYPH JJ")
        'two-year-old'
        >>> r.read_line("-LRB- China -RRB-\t-LRB- NNP -RRB-")
        '( China )'
        """
        try:
            len(line.split('\t')) == 2
        except Exception:
            print('Warning: line wrongly formatted. Should be tab-separated.')

        (raw_text, pos_tags) = line.split('\t')
        tokens = raw_text.split()
        tags = pos_tags.split()

        try:
            len(tokens) == len(tags)
        except Exception:
            print('Warning: length of tokens and tags not the same')

        # Replace brackets with proper symbols
        if '-LRB-' in tags:
            lrb_indexes = [i for i, j in enumerate(tags) if j == '-LRB-']
            for i in lrb_indexes:
                tokens[i] = '('
        if '-RRB-' in tags:
            rrb_indexes = [i for i, j in enumerate(tags) if j == '-RRB-']
            for i in rrb_indexes:
                tokens[i] = ')'

        # Remove spaces for HYPHens
        if 'HYPH' in tags:
            hyph_indexes = [i for i, j in enumerate(tags) if j == 'HYPH']
            # Iterate from end of index list (to avoid indexing issues)
            for i in reversed(hyph_indexes):
                # Remove spaces around hyphen (merge tokens before and after)
                tokens[i-1:i+2] = [''.join(tokens[i-1:i+2])]

        return ' '.join(tokens)
