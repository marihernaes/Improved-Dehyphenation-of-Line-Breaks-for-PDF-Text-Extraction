import sys
import os


class OntonotesConllToTsv:
    """
    For an ontonotes gold_conll file, convert it to a tsv. format, suitable
    for what we will use it for:

    <raw sentence (space separated)> <TAB> <pos tags (space separated)>
    """

    def conll_to_tsv(self, input_conll_file, output_tsv_file):
        """
        Reads a single conll file and writes it, reformatted, to a tsv file.
        """
        with open(input_conll_file) as input:
            paragraphs = []
            sentences = []
            words = []
            tags = []
            for line in input:
                token = line.strip().split()

                # For normal lines (without #begin or #end)
                if len(token) > 5:
                    # The raw word
                    words.append(token[3])
                    # The tag of this word
                    tags.append(token[4])
                # For empty line
                elif len(token) == 0:
                    sentences.append((words, tags))
                    words = []
                    tags = []
                # For line #end
                elif len(token) == 2:
                    paragraphs.append(sentences)
                    sentences = []

        with open(output_tsv_file, 'w') as output:
            for p in paragraphs:
                for (words, tags) in p:
                    output.write('%s\t%s\n' %
                                 (' '.join(words), ' '.join(tags)))
                output.write("\n")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("""Usage: python3 ontonotes_to_json.py"""
              """ <directory with gold_conll files> <target directory>""")
        sys.exit()

    conll_path = sys.argv[1]
    target_path = sys.argv[2]

    o = OntonotesConllToTsv()

    for root, dirs, files in os.walk(conll_path):
        for name in files:
            if name.endswith(".gold_conll"):
                # Copy the file into a directory, annotating the origin
                origin = root.find("ontonotes")
                subfolder = root[origin + 10:]
                target_folder = target_path + subfolder + '/'
                # If the subfolder does not exist, create it
                if not os.path.exists(target_folder):
                    os.makedirs(target_folder)
                # Convert the file to an appropriate tsv format
                o.conll_to_tsv(root + '/' + name,
                               target_folder + name[:-10] + 'tsv')
