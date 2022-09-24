# Source: https://www.analyticsvidhya.com/blog/2018/04/a-comprehensive-guide\
# -to-understand-and-implement-text-classification-in-python/
# and: https://github.com/kk7nc/Text_Classification/blob/master/README.rst#\
# random-forest Chapter CRF
# Author: Mari Hernaes.
"""
Train a Conditional Random Fields model on the problem with hyphenated words.
Input: a corpus in the format <label> <prefix> <suffix>, where the prefix
and suffix are the result of a hyphenation algorithm on a word.

Saves the model in a pickle file.

NOTE: this is a NEWER version of the algorithm, implementing the *correct* word
shape features. Also, name indicates the training algorithm actually used.
(see http://www.chokkan.org/software/crfsuite/manual.html#idp8849121424)
"""

import sklearn_crfsuite
import pickle
import sys
import pdb
import re


def run(data_file, model_output):
    # Load the training data
    data = open(data_file).read()
    labels, chars = [], []
    for i, line in enumerate(data.split("\n")):
        if line:
            content = line.split('\t')
            labels.append(content[0])
            chars.append(' '.join(content[1:]))

    train_x = chars
    train_y = labels

    # Create feature dictionaries for the training data
    xtrain_feature_dicts = [extract_features(x) for x in train_x if x]

    # Create a CRF model
    crf = sklearn_crfsuite.CRF(
        algorithm='lbfgs',
        max_iterations=100,
        all_possible_transitions=True
    )

    print("Fitting CRF model on feature dicts")
    # THE FITTING FROM SKLEARN_CRFSUITE CAN NOT HANDLE INTEGERS / NUMPY ARRAYS
    # FOR THE PREDICTIONS. DO NOT LABELENCODE.. WRITE ONE-DIGIT STRING LABELS
    crf.fit(xtrain_feature_dicts, train_y)

    print('Saving model to file')
    # Save the model to a file in binary mode
    with open(model_output, 'wb') as modelout:
        pickle.dump(crf, modelout, protocol=pickle.HIGHEST_PROTOCOL)
        print('Done. File %s written.' % modelout)


def extract_features(tpl):
    """
    For a tuple (prefix, suffix), extract the feature vectors. Look up
    the word in the word stem and return the tuple not as strings, but
    as corresponding numbers.
    """
    if len(tpl.split()) != 2:
        pdb.set_trace()

    (prefix, suffix) = tpl.split()
    all_features = {'word-shape': get_word_shape(prefix, suffix)}
    all_features.update(standard_prefix_features(prefix))
    all_features.update(standard_suffix_features(suffix))
    return [all_features]


def get_word_shape(prefix, suffix):
    """ For a prefix and suffix, create the word shape. See doctests

    >>> get_word_shape('high', 'quality')
    'xxxx-xxxxxxx'
    >>> get_word_shape('19th-cen','tury')
    'xxxx-xxx-xxxx'
    >>> get_word_shape('high-as-a', 'kite')
    'xxxx-xx-x-xxxx'
    """
    return re.sub(r'[^-]', 'x', prefix + '-' + suffix)


def standard_prefix_features(prefix):
    """
    For a prefix, return a standard set of features. For example
    the two last bigrams, the prefix in lowercase, and so on.
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
                # 'p:hasdigit': True if re.search(r'\d+', prefix) else False,
                'p:hashyphen': True if prefix.find('-') > -1 else False,
                'p:lower': prefix.lower()}
    features.update(bigrams)
    return features


def standard_suffix_features(suffix):
    """
    For a suffix, return a standard set of features. For example
    the two first bigrams, the suffix in lowercase, and so on.
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
                # 's:hasdigit': True if re.search(r'\d+', suffix) else False,
                's:hashyphen': True if suffix.find('-') > -1 else False,
                's:lower': suffix.lower()}
    features.update(bigrams)
    return features


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("""Usage: python3 crf_train_model_hyphenation.py """
              """<corpus_file> <model_output.pkl>""")
        sys.exit()

    input = sys.argv[1]
    model_output = sys.argv[2]

    sys.stdout.write("\nProcessing: %s \n" % (input))
    run(input, model_output)
    sys.stdout.write("Done.\n")
