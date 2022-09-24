# Copyright 2019, University of Freiburg,
# Chair of Algorithms and Data Structures.
# Author: Mari Hernaes.

import re


class ReformatClueweb:
    """
    A class to read lines from the Clueweb dataset. The data set consists of
    one sentence pro line, but it has Named Entity Tags, which needs to be
    removed in order to obtain the raw text.
    """

    def read_line(self, line):
        r"""
        Reads a line from the Clueweb data set and returns a normal sentence,
        e.g. without of NER tags and such.

        >>> r = ReformatClueweb()
        >>> r.read_line("Don't you want to see [m.04abc2|Tom]?")
        "Don't you want to see Tom?"
        >>> r.read_line("[m.0h7h6|Toronto] ’s [m.09qj1|China Town] .")
        'Toronto ’s China Town .'
        >>> r.read_line("seventy-year-old - wow!") # Interruptor hyphen en dash
        'seventy-year-old — wow!'
        """

        # For [ followed by m.0ssef and | (group) ], keep group 1 (r'\1').
        line = re.sub(r'\[[a-z]\.[^\|]+\|([^\]]+)\]', r'\1', line)

        # In clueweb, the hyphens and dashes are not consistent. Replace hyphen
        # with en dash when it is (most probably) used as an interruptor
        line = re.sub(r'\s-\s', ' \u2014 ', line)

        return line.strip()
