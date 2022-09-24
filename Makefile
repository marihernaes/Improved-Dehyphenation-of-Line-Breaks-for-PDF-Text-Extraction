# General
TEST_CMD = python3 -m doctest
CHECKSTYLE_CMD = flake8

# Main scripts
RUN_SCRIPT = scripts/run/process_file.py
EVAL_BASELINE_SCRIPT = scripts/evaluate/evaluate_baselines_on_file_confusion_matrix.py
EVAL_LOGREG_SCRIPT = scripts/evaluate/crf_evaluate.py
EVAL_LANGMOD_SCRIPT = scripts/evaluate/language_model_evaluate.py
HYPH_SCRIPT = scripts/hyphenate/process_hyphenation.py
CORPUS_SCRIPT = scripts/other/create_corpus.py

# Main data sets
DATA_SET_CLUEWEB_SMALL = extern/data/clueweb-small.tsv
DATA_SET_WIKIPEDIA = extern/data/prepared_wikipedia_hyphenated/wikipedia-extract.tsv
DATA_SET = $(DATA_SET_CLUEWEB_SMALL)  # Default data set clueweb small

# Main result directory file name
RESULT_DIR = extern/data/generated_results_text
RESULT_NAME = $(RESULT_DIR)/$(basename $(notdir $(DATA_SET)))_$(basename $(notdir $(VOC)))
EVAL_DIR = extern/data/generated_evaluation
EVAL_NAME = $(EVAL_DIR)/$(basename $(notdir $(DATA_SET)))_$(basename $(notdir $(VOC)))
EVAL_CORPUS_FILE_NAME = $(EVAL_DIR)/$(basename $(notdir $(TEST_CORPUS)))_$(basename $(notdir $(MODEL)))
NEW_CORPUS_DIR = extern/data/generated_corpus
NEW_CORPUS_NAME = $(NEW_CORPUS_DIR)/corpus

# Input output directories
INPUT_DIR = extern/data/clueweb_sentences/
OUTPUT_DIR = extern/data/generated_hyphenated_dataset/
HYPHEN_DISTANCE = 13

# Main vocabularies and such
VOC-CLUEWEB = extern/data/prepared_vocabs/clueweb-number-voc
VOC-ONTONOTES = extern/data/prepared_vocabs/ontonotes-number-voc
VOC-IMDB = extern/data/prepared_vocabs/imdb-voc
VOC = $(VOC-CLUEWEB)  # Default vocabulary set to ontonotes

MODEL = extern/data/prepared_models/crf-wikipedia.pkl
MODEL_ONTO = extern/data/prepared_models/crf-ontonotes-full.pkl
TEST_CORPUS = extern/data/prepared_corpus/wikipedia-extract-corpus

help:
	@echo "\nWelcome."
	@echo "This work is about dehyphenation of line breaks for text extraction."
	@echo "The input is a word, hyphenated with a special character"
	@echo "The ouptut is the word with either a hyphen or nothing on this place"
	@echo ""
	@echo "There are three approaches:"
	@echo "1) BASELINE. Use a vocabulary to look up the hyphenated and non-"
	@echo "hyphenated word. Choose the variant with the most common spelling."
	@echo "2) LOGISTIC REGRESSION. Use a model with prefix- and suffix features"
	@echo "to decide if the word should have a hyphen or not."
	@echo "3) LANGUAGE MODEL. Use a bi-LSTM language model on a sentence, and the"
	@echo "character probabilities to decide if a word should be hyphenated or not."
	@echo ""
	@echo "This makefile has targets to reproduce this work."
	@echo "Try out:"
	@echo "	- test"
	@echo "	- checkstyle"
	@echo "	- clean"
	@echo "	- or all: test checkstyle"
	@echo "to check the style and doctest of the scripts."
	@echo ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::"
	@echo "We 'HYPHENATE' a dataset of sentences using the following targets:"
	@echo "	- hyphenate-clueweb"
	@echo "	- hyphenate-ontonotes"
	@echo "	- hyphenate-wikipedia"
	@echo "To access help information, please use a target with the suffix -help"
	@echo "The targets are different due to specific data-set depenent problems."
	@echo "For example: mixed POS-TAGS and words in ontonotes."
	@echo "*You can use hyphenate-clueweb to hyphenate any kind of data set.*"
	@echo ""
	@echo "NOTE: you can go directly to the 'run' or 'evaluate' step. We have"
	@echo "prepared different hyphenated datasets in extern/data/"
	@echo ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::"
	@echo "We 'RUN' the approaches on a data set and writes the output (the de-"
	@echo "hyphenated data set without the special hyphen character) to a file."
	@echo "There are four targets, for each, there is help information:"
	@echo "	- run-baseline-basic"
	@echo "	- run-baseline-supplemented"
	@echo "	- run-logistic-regression"
	@echo "	- run-language-model"
	@echo "To access help information, please use a target with the suffix -help"
	@echo ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::"
	@echo "We 'EVALUATE' the approaches on a data set and write the result as"
	@echo "confusion matrices. For the baseline approaches, there is even more"
	@echo "information: about mistake categories and ambiguous spellings."
	@echo "There are four targets, for each, there is help information:"
	@echo "	- evaluate-baseline-basic"
	@echo "	- evaluate-baseline-supplemented"
	@echo "	- evaluate-logistic-regression"
	@echo "	- evaluate-language-model"
	@echo "To access help information, please use a target with the suffix -help"
	@echo ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::"
	@echo "We 'CREATE A CORPUS' (suitable for machine learning) from a hyphenated"
	@echo "dataset (that is, the output of the 'hyphenate' targets). All hyphen-"
	@echo "ated words are splitted at the special hyphen symbol, and written to"
	@echo "the corpus as <label>tab<prefix>tab<suffix>, where label 0 is 'remove"
	@echo "hyphen' and 1 is 'keep it', depending on expected output."
	@echo "	- create-a-corpus"
	@echo "To access help information, please use a target with the suffix -help"
	@echo ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::"
	@echo ""

all: test checkstyle

test:
	$(TEST_CMD) scripts/run/*.py  # Doctest the run scripts
	$(TEST_CMD) scripts/evaluate/*.py  # Doctest the evaluation scripts
	$(TEST_CMD) scripts/hyphenate/*.py  # Doctest the hyphenation scripts
	$(TEST_CMD) scripts/other/*.py  # Doctest the other scripts
	$(TEST_CMD) scripts/no-make-target/*.py

clean:
	rm -f scripts/run/*.pec  # Clean the run folder
	rm -rf scripts/run/__pycache__
	rm -f scripts/evaluate/*.pec  # Clean the evaluation folder
	rm -rf scripts/evaluate/__pycache__
	rm -f scripts/hyphenate/*.pec  # Clean the hyphenate folder
	rm -rf scripts/hyphenate/__pycache__
	rm -f scripts/other/*.pec  # Clean the other folder
	rm -rf scripts/other/__pycache__
	rm -f scripts/no-make-target/*.pec  # Clean the no-make-target folder
	rm -rf scripts/other/__pycache__

checkstyle:
	$(CHECKSTYLE_CMD) scripts/run/*.py  # Stylecheck the run scripts
	$(CHECKSTYLE_CMD) scripts/evaluate/*.py  # Stylecheck the evaluation scripts
	$(CHECKSTYLE_CMD) scripts/hyphenate/*.py  # Stylecheck the hyphenation scripts
	$(CHECKSTYLE_CMD) scripts/other/*.py  # Stylecheck the other scripts
	$(CHECKSTYLE_CMD) scripts/no-make-target/*.py

dummy:
	@echo "I do not want the comment underneath to appear with the checkstyle"
	# ===========================================================================
	# RUN targets
	# ===========================================================================

run-baseline-basic:
	python3 $(RUN_SCRIPT) 'base' $(VOC) $(DATA_SET) $(RESULT_NAME)_result-text_baseline-basic.tsv

run-baseline-basic-help:
	@echo "\nThis target runs the basic baseline version."
	@echo "It does not handle numbers, in contrast to run-baseline-supplemented."
	@echo "Variables:"
	@echo "	- VOC the vocabulary. (default: /prepared_vocabs/clueweb. options: extern/data/prepared_vocabs)"
	@echo "	- DATA_SET a hyphenated data set.(default: clueweb-small.tsv. options: extern/data)"
	@echo "	- RESULT_DIR directory for result. (default: generated-results-text)"
	@echo "	- RESULT_NAME name of the output file. (default: <result_dir>/<data_set>_<vocabulary>_result-text_baseline-basic.tsv)"

run-baseline-supplemented:
	python3 $(RUN_SCRIPT) 'base2' $(VOC) $(DATA_SET) $(RESULT_NAME)_result-text_baseline-supplemented.tsv

run-baseline-supplemented-help:
	@echo "\nThis target runs the supplemented baseline version."
	@echo "It handles numbers, in contrast to run-baseline-basic."
	@echo "Variables: "
	@echo "	- VOC the vocabulary. (default: /prepared_vocabs/clueweb. options: extern/data/prepared_vocabs)"
	@echo "	- DATA_SET a hyphenated data set. (default: clueweb-small.tsv. options: extern/data)"
	@echo "	- RESULT_DIR (directory for result. (default: generated-results-text)"
	@echo "	- RESULT_NAME name of the output file. (default: <data_set>_<vocabulary>_result-text_baseline-supplemented.tsv)"

run-logistic-regression: RESULT_NAME=$(RESULT_DIR)/$(basename $(notdir $(DATA_SET)))_$(basename $(notdir $(MODEL)))
run-logistic-regression:
	python3 $(RUN_SCRIPT) 'logreg' $(MODEL) $(DATA_SET) $(RESULT_NAME)_result-text_logistic-regression.tsv

run-logistic-regression-help:
	@echo "\nThis target runs the logistic regression."
	@echo "Variables: "
	@echo "	- MODEL the crfsuite-style model. (default: /models/crf-wikipedia. options: extern/data/prepared_models)"
	@echo "	- DATA_SET a hyphenated data set. (default: prepared_corpus/clueweb-small-corpus. options: extern/data/prepared_corpus)"
	@echo "	- RESULT_DIR (directory for result. (default: generated-results-text)"
	@echo "	- RESULT_NAME name of the output file. (default: <data_set>_<model>_result-text_logistic-regression.tsv)"

run-language-model: RESULT_NAME=$(RESULT_DIR)/$(basename $(notdir $(DATA_SET)))
run-language-model:
	python3 $(RUN_SCRIPT) 'langmod' x $(DATA_SET) $(RESULT_NAME)_result-text_language-model.tsv

run-language-model-help:
	@echo "\nThis target runs the language model."
	@echo "Variables: "
	@echo "	- DATA_SET a hyphenated data set. (default: clueweb-small.tsv. options: extern/data)"
	@echo "	- RESULT_DIR directory for result. (default: generated-results-text)"
	@echo "	- RESULT_NAME name of the output file. (default: <data_set>_result-text_language-model.tsv)"

dummy-three:
	@echo "I do not want the comment underneath to appear with the checkstyle"

	# ===========================================================================
	# EVALUATE targets
	# ===========================================================================
	EVAL_TEXT_FILE_NAME = $(EVAL_DIR)/$(basename $(notdir $(DATA_SET)))_$(basename $(notdir $(VOC)))
	EVAL_CORPUS_FILE_NAME = $(EVAL_DIR)/$(basename $(notdir $(TEST_CORPUS)))_$(basename $(notdir $(MODEL)))

evaluate-baseline-basic:
	python3 $(EVAL_BASELINE_SCRIPT) '1' $(DATA_SET) $(VOC) $(EVAL_NAME)_evaluation.txt

evaluate-baseline-basic-help:
	@echo "\nThis target evaluates the basic baseline version."
	@echo "It does not handle numbers, in contrast to run-baseline-supplemented."
	@echo "Variables:"
	@echo "	- VOC the vocabulary. (default: /prepared_vocabs/clueweb. options: extern/data/prepared_vocabs)"
	@echo "	- DATA_SET a hyphenated data set. (default: clueweb-small.tsv. options: extern/data)"
	@echo "	- EVAL_DIR directory for result. (default: generated_evaluation)"
	@echo "	- EVAL_NAME name of the output file. (default: <data_set>_<vocabulary>_evaluation.txt)"

evaluate-baseline-supplemented:
	python3 $(EVAL_BASELINE_SCRIPT) '2' $(DATA_SET) $(VOC) $(EVAL_NAME)_evaluation.txt

evaluate-baseline-supplemented-help:
	@echo "\nThis target evaluates the supplemented baseline version."
	@echo "It handles numbers, in contrast to run-baseline-basic."
	@echo "Variables:"
	@echo "	- VOC the vocabulary. (default: /prepared_vocabs/clueweb. options: extern/data/prepared_vocabs)"
	@echo "	- DATA_SET a hyphenated data set. (default: clueweb-small.tsv. options: extern/data)"
	@echo "	- EVAL_DIR directory for result. (default: generated_evaluation)"
	@echo "	- EVAL_NAME name of the output file. (default: <data_set>_<vocabulary>_evaluation.txt)"

evaluate-logistic-regression: EVAL_NAME = $(EVAL_DIR)/$(basename $(notdir $(TEST_CORPUS)))_$(basename $(notdir $(MODEL)))
evaluate-logistic-regression:
	python3 $(EVAL_LOGREG_SCRIPT) $(TEST_CORPUS) $(MODEL_ONTO) $(EVAL_NAME)_evaluation_confusion-matrix.txt

evaluate-logistic-regression-help:
	@echo "\nThis target evaluates the logistic regression."
	@echo "Variables: "
	@echo "	- MODEL_ONTO the crfsuite-style model. (default: crf-ontonotes-allwords. options: extern/data/prepared_models)"
	@echo "	- TEST_CORPUS a corpus <label>tab<prefix>tab<suffix>. (default: wikipedia-extract-corpus. options: extern/data/prepared_corpus"
	@echo "	- EVAL_DIR directory for result. (default: generated_evaluation)"
	@echo "	- EVAL_NAME name of the output file. (default: <test_corpus>_<model>_evaluation.txt)"

evaluate-language-model:
	python3 $(EVAL_LANGMOD_SCRIPT) --benchmark_file $(DATA_SET)

evaluate-language-model-help:
	@echo "\nThis target evaluates the language model."
	@echo "Variables: "
	@echo "	- DATA_SET a hyphenated data set. (default: clueweb-small. options: extern/data)"
	@echo "Note: the evaluation is not printed to a file but to the terminal"

dummy-two:
		@echo "I do not want the comment underneath to appear with the checkstyle"

	# ===========================================================================
	# HYPHENATE targets
	# ===========================================================================
hyphenate-clueweb:
	python3 $(HYPH_SCRIPT) $(INPUT_DIR) $(OUTPUT_DIR) 'c' $(HYPHEN_DISTANCE)

hyphenate-clueweb-help:
	@echo "\nThis targets hyphenates clueweb (or another dataset)"
	@echo "Variables: "
	@echo "	- INPUT_DIR the (unhyphenated) data set directory. (default: clueweb_sentences)"
	@echo "	- OUTPUT_DIR the hyphenated data set directory. (default: generated_hyphenated_dataset)"
	@echo "	- HYPHEN_DISTANCE the distance between successful hyphenations (default: 13)"

hyphenate-ontonotes:	INPUT_DIR=extern/data/ontonotes_sentences
hyphenate-ontonotes:
	python3 $(HYPH_SCRIPT) $(INPUT_DIR) $(OUTPUT_DIR) 'o' $(HYPHEN_DISTANCE)

hyphenate-ontonotes-help:
	@echo "\nThis targets hyphenates ontonotes (in the format 'sentence tab pos-tags')"
	@echo "Variables: "
	@echo "	- INPUT_DIR the (unhyphenated) data set directory. (default: ontonotes_all_sentences.tsv)"
	@echo "	- OUTPUT_DIR the hyphenated data set directory. (default: generated_hyphenated_dataset)"
	@echo "	- HYPHEN_DISTANCE the distance between successful hyphenations (default: 13)"

hyphenate-wikipedia:	INPUT_DIR=extern/data/wikipedia_paragraphs/
hyphenate-wikipedia:
	python3 $(HYPH_SCRIPT) $(INPUT_DIR) $(OUTPUT_DIR) 'w' $(HYPHEN_DISTANCE)

hyphenate-wikipedia-help:
	@echo "\nThis targets hyphenates wikipedia."
	@echo "Variables: "
	@echo "	- INPUT_DIR the (unhyphenated) data set directory. (default: wikipedia_paragraphs)"
	@echo "	- OUTPUT_DIR the hyphenated data set directory. (default: generated_hyphenated_dataset)"
	@echo "	- HYPHEN_DISTANCE the distance between successful hyphenations (default: 13)"

	# ===========================================================================
	# CREATE targets
	# ===========================================================================
create-a-corpus:
	python3 $(CORPUS_SCRIPT) $(DATA_SET) $(NEW_CORPUS_NAME)

create-a-corpus-help:
	@echo "\nThis target creates a corpus from a hyphenated file of sentences."
	@echo "Variables: "
	@echo "	- DATA_SET a hyphenated data set. (default: clueweb-small.tsv. options: extern/data)"
	@echo "	- NEW_CORPUS_NAME the name of the output. (default: generated_corpus/corpus)"
