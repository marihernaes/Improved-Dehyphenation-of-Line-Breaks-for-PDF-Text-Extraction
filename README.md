# Improved-Dehyphenation-of-Line-Breaks-for-PDF-Text-Extraction
Bachelor's Thesis with different python scripts for parsing and evaluation big data sets.

Words in layout-based documents can contain hyphens that divide the word into two parts across two lines. PDF documents only store information about individual
characters, which makes it difficult to extract text correctly. Words which are hyphenated at the end of a line are especially problematic because in English there are some words where the hyphen should be kept, while others need to be merged.

For example, “high-quality” can be a compound word. If this word splits on the hyphen across two lines, then the hyphen should be retained in the extracted text. The correct
dehyphenation of line breaks requires the recognition of either words or sequences of characters. In this thesis, vocabulary-based baseline algorithms, logistic regression
on the word level and a bi-LSTM Language Model on the character level are used to solve this problem.
