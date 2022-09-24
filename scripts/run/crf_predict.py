# Source: https://www.analyticsvidhya.com/blog/2018/04/a-comprehensive-guide\
# -to-understand-and-implement-text-classification-in-python/
# and: https://github.com/kk7nc/Text_Classification/blob/master/README.rst#\
# random-forest Chapter CRF
# Author: Mari Hernaes.
"""
Uses a Conditional Random Fields model on the problem with hyphenated words.
Input: a joblib file with the crf model. The class uses this model to predict.
"""

import pickle


class CrfPredict:
    """
    Loads the crf model and uses this to predict the label of single words.
    """

    def __init__(self, hyphen_symbol='\u0387'):
        """ Loads the model from a pkl file only once """
        self.hyphen = hyphen_symbol
        self.model = None

    def load_model_file(self, model_file):
        """Loads the model """
        with open(model_file, 'rb') as model:
            self.model = pickle.load(model)

    def predict_word(self, hyphenated_word):
        """Predicts if a hyphenated word should have hyphen (1) or not (0)"""
        test_x = hyphenated_word.replace(self.hyphen, ' ')
        test_x_features = [self.extract_features(test_x)]

        prediction = self.model.predict(test_x_features)
        return prediction[0][0]

    def extract_features(self, tpl):
        """
        For a tuple (prefix, suffix), extract the feature vectors. Look up
        the word in the word stem and return the tuple not as strings, but
        as corresponding numbers.
        """
        (prefix, suffix) = tpl.split()
        wordshape = ('%s-%s' % ('x' * len(prefix), 'x' * len(suffix)))
        all_features = {'word-shape': wordshape}
        all_features.update(self.standard_prefix_features(prefix))
        all_features.update(self.standard_suffix_features(suffix))
        return [all_features]

    def standard_prefix_features(self, prefix):
        """
        For a prefix, return a standard set of features. For example
        the two last bigrams, the prefix in lowercase, and so on.

        >>> c = CrfPredict()
        >>> sorted(c.standard_prefix_features('13th').items())
        ... # doctest: +NORMALIZE_WHITESPACE
        [('p:-1bigram', 'th'), ('p:-2bigram', '3t'), ('p:-3bigram', '13'),
        ('p:hashyphen', False), ('p:isdigit', False),
        ('p:isuppercase', False), ('p:lower', '13th')]
        """

        bigrams = {}
        if len(prefix) >= 2:
            bigrams.update({'p:-1bigram': prefix[-2:].lower()})
            if len(prefix) >= 3:
                bigrams.update({'p:-2bigram': prefix[-3:-1].lower()})
                if len(prefix) >= 4:
                    bigrams.update({'p:-3bigram': prefix[-4:-2].lower()})

        features = {'p:isuppercase': prefix.isupper(),
                    'p:isdigit': True if prefix.isdigit() else False,
                    # 'p:hasdigit': True if re.search(r'\d+', prefix)
                    'p:hashyphen': True if prefix.find('-') > -1 else False,
                    'p:lower': prefix.lower()}
        features.update(bigrams)
        return features

    def standard_suffix_features(self, suffix):
        """
        For a suffix, return a standard set of features. For example
        the two first bigrams, the suffix in lowercase, and so on.

        >>> c = CrfPredict()
        >>> sorted(c.standard_suffix_features('er').items())
        ... # doctest: +NORMALIZE_WHITESPACE
        [('s:+1bigram', 'er'), ('s:hashyphen', False),
        ('s:isdigit', False), ('s:isuppercase', False), ('s:lower', 'er')]
        """
        bigrams = {}
        if len(suffix) >= 2:
            bigrams.update({'s:+1bigram': suffix[:2].lower()})
            if len(suffix) >= 3:
                bigrams.update({'s:+2bigram': suffix[1:3].lower()})
                if len(suffix) >= 4:
                    bigrams.update({'s:+3bigram': suffix[2:4].lower()})

        features = {'s:isuppercase': suffix.isupper(),
                    's:isdigit': True if suffix.isdigit() else False,
                    # 's:hasdigit': True if re.search(r'\d+', suffix)
                    's:hashyphen': True if suffix.find('-') > -1 else False,
                    's:lower': suffix.lower()}
        features.update(bigrams)
        return features
