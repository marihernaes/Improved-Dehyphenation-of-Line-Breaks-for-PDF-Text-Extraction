# Copyright 2019, University of Freiburg,
# Chair of Algorithms and Data Structures.
# Author: Mari Hernaes.


class ReformatWikipedia:
    """
    A class to read lines from the Wikipedia dataset. The data set consists of
    one sentence pro line, but it has Named Entity Tags, which needs to be
    removed in order to obtain the raw text.
    """

    def read_line(self, line):
        r"""
        Reads a line from the Wikipedia data set and returns a normal sentence,
        e.g. without of NER tags and such.

        >>> r = ReformatWikipedia()
        >>> r.read_line("[[Niokolo-Koba")
        'Niokolo-Koba'
        """

        # Remove square brackets
        line = line.replace('[', '')
        line = line.replace(']', '')

        return line.strip()
