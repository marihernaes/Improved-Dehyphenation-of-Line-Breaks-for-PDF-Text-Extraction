# Source: https://www.analyticsvidhya.com/blog/2018/04/a-comprehensive-guide\
# -to-understand-and-implement-text-classification-in-python/
# and: https://github.com/kk7nc/Text_Classification/blob/master/README.rst#\
# random-forest Chapter CRF
# Author: Mari Hernaes.
"""
Uses a Conditional Random Fields model on the problem with hyphenated words.
Input: a joblib file with the crf model, and a data set to test on.
"""

import pickle
import sys
import pdb


def run(test_file, model_file, result_file):
    # Load the model from file in binary mode
    with open(model_file, 'rb') as model:
        crf = pickle.load(model)

    # Load test data
    print('Loading test data')
    testdata = open(test_file).read()
    test_x, test_y = [], []
    for i, line in enumerate(testdata.split("\n")):
        if line:
            content = line.split('\t')
            test_y.append(content[0])
            test_x.append(' '.join(content[1:]))
    print('Done')

    # Create feature dicts for test data
    xtest_feature_dicts = [extract_features(x) for x in test_x if x]

    # Make predictions on test data
    test_predictions = crf.predict(xtest_feature_dicts)

    # Print 10 first the predictions, to visualize
    for i, pred in enumerate(test_predictions[:10]):
        print("Prediction: {} Word: {}".format(pred, test_x[i]))
    print('\n')

    # Evaluate using own method
    print('\nEvaluation of self-made test dataset:\n')
    results = evaluate_accuracy(test_predictions, test_y)
    print(results)

    # Save the results to a file
    with open(result_file, "w+", encoding="utf-8") as rf:
        rf.write(results)


def extract_features(tpl):
    """
    For a tuple (prefix, suffix), extract the feature vectors. Look up
    the word in the word stem and return the tuple not as strings, but
    as corresponding numbers.
    """
    if len(tpl.split()) != 2:
        pdb.set_trace()

    (prefix, suffix) = tpl.split()
    wordshape = ('%s-%s' % ('x' * len(prefix), 'x' * len(suffix)))
    all_features = {'word-shape': wordshape}
    all_features.update(standard_prefix_features(prefix))
    all_features.update(standard_suffix_features(suffix))
    return [all_features]


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


def evaluate_accuracy(predictions, test_y):
    if len(predictions) != len(test_y):
        pdb.set_trace()

    # Initialize counters for confusion matrix.
    # d: delete the hyphen; k: keep the hyphen.
    # For example: num_d_d = number_predicted_delete_expected_delete
    num_d_d, num_d_k, num_k_d, num_k_k = 0, 0, 0, 0

    # Compare the predicted output with the expected output
    for i, y in enumerate(test_y):
        # 0: delete the hyphen; 1: keep the hyphen.
        if predictions[i][0] == '0':
            if y == '0':
                num_d_d += 1
            elif y == '1':
                num_d_k += 1
        elif predictions[i][0] == '1':
            if y == '0':
                num_k_d += 1
            elif y == '1':
                num_k_k += 1
        else:
            pdb.set_trace()

    accuracy = (num_d_d + num_k_k) / (num_d_d + num_d_k + num_k_d + num_k_k)

    # Create the evaluation values
    evl = []
    evl.append("Accuracy:                       %.2f%%" % (accuracy * 100))
    evl.append("Accuracy 'expected non-hyphen': %.2f%%" % (
        100 * num_d_d / (num_d_d + num_k_d)))
    evl.append("Accuracy 'expected hyphen':     %.2f%%" % (
        100 * num_k_k / (num_d_k + num_k_k)))
    evl.append("")
    evl.append("Confusion Matrix:")
    evl.append("                expected '':   expected '-':")
    evl.append("predicted '' :  %s     %s" % (
        str(num_d_d).rjust(11), str(num_d_k).rjust(11)))
    evl.append("predicted '-':  %s     %s" % (
        str(num_k_d).rjust(11), str(num_k_k).rjust(11)))
    result_string = '\n'.join(evl)

    return result_string


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("""Usage: python3 crf_model_hyphenation.py """
              """<testcorpus_file> <model_input.pkl> <result_file> """)
        sys.exit()

    test_file = sys.argv[1]
    model_file = sys.argv[2]
    result_file = sys.argv[3]

    sys.stdout.write("\nProcessing: %s \n" % (test_file))
    run(test_file, model_file, result_file)
    sys.stdout.write("Done.\n")
