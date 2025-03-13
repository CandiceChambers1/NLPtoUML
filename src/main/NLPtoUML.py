# Spacy Imports
import spacy
from spacy.lang.en import English

# nltk Imports
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize

#plantUML Imports
import plantuml
from plantuml import PlantUML

# Other Imports
import string
from os.path import abspath
import collections
from collections import defaultdict

#nltk downloads
nltk.download('punkt_tab')
nltk.download('averaged_perceptron_tagger_eng')
nltk.download('wordnet')
nltk.download('omw-1.4')

def tokenAndPOS_Tags(sent):
    nlp = English()
    token_sentence = nlp(sent)
    # Allows the tokenizing of special words, this way words containing all
    # symbols outside of the ones outlined are not seperated
    # Eg: Inhibited_count>=2
    suffixes = nlp.Defaults.suffixes + [r"\-|\|\$", ]
    suffix_regex = spacy.util.compile_suffix_regex(suffixes)
    nlp.tokenizer.suffix_search = suffix_regex.search

    doc = nlp(sent)
    token_sentence = []
    # Extract the token and store them in the token_sentence list
    for token in doc:
        token_sentence.append(token.text)

    # POS Tag the tokens
    pos_tag_token = nltk.pos_tag(token_sentence)

    return token_sentence, pos_tag_token


# Noun Extraction functions
def nounExtraction(tag_tokens):
    # Noun Extraction (only extracting Proper Nouns)
    nltk_nouns = []
    for index, tuple in enumerate(tag_tokens):
        if tuple[1] == 'NNP':
            nltk_nouns.append(tuple[0])
    return nltk_nouns


# List of Synonyms for consist and connect
# This is used oppose the stemming as certain Proper Nouns where being truncated
def synonyms_lists():
    consist_synonyms = ['consist', 'consists', 'include', 'includes', 'comprise', 'comprises']
    connect_synonyms = ['connection', 'connections', 'connects', 'connect']
    input_synonyms = ['input', 'accepts', 'accept']

    return consist_synonyms, connect_synonyms, input_synonyms


# Editing or creating text file if it doesn't exists
# Creating the code for plantuml to generate a component based diagram

def staticPlantumlCode(text):
    # Used to tokenize a sentence
    doc = sent_tokenize(text)
    main_sub_component = []

    f = open(r"/src/uml/s_model_specs.txt", "w")
    # Iterate sentence-by-sentence then word-by-word
    for sent in doc:
        # Call Tokenize and Stemming and POS Tag Function
        token_sentence, pos_tag_token = tokenAndPOS_Tags(sent)

        # Call Noun Extraction Function
        # First noun is the main noun, the other nouns are its associations(inputs,
        # sub-components and outputs)
        nltk_nouns = nounExtraction(pos_tag_token)

        # Used to increment the number of elements in the list of nouns
        i = 1

        # Call synonyms
        consist_synonyms, connect_synonyms, input_synonyms = synonyms_lists()

        # create sets variable to check if consist synonyms are being used
        t_sentence_set = set(token_sentence)
        consist_set = set(consist_synonyms)
        connect_set = set(connect_synonyms)
        input_set = set(input_synonyms)
        # If any synonym to consist exsists in the token list
        if (consist_set & t_sentence_set):
            while (i < len(nltk_nouns)):
                main_sub_component = nltk_nouns[1:]
                i = i + 1

                # If any synonym to connect exsists in the token list
        if (connect_set & t_sentence_set):
            while (i < len(nltk_nouns)):
                # Find the index of the first noun extracted in the main_sub_component
                # to prioritize order
                if (main_sub_component.index(nltk_nouns[0]) >
                        main_sub_component.index(nltk_nouns[i])):
                    f.write(f"[{nltk_nouns[i]}]-[{nltk_nouns[0]}]\n")
                else:
                    f.write(f"[{nltk_nouns[0]}]-[{nltk_nouns[i]}]\n")
                i = i + 1

        # If any synonyms to input is in the token
        if (input_set & t_sentence_set):
            # If input and clock is in the token
            if "clock" in token_sentence:
                while (i < len(nltk_nouns)):
                    f.write(f"{nltk_nouns[0]}<-up-({nltk_nouns[i]})\n")
                    i = i + 1
            # If input and boolean is in the token
            elif "boolean" in token_sentence:
                while (i < len(nltk_nouns)):
                    f.write(f"({nltk_nouns[i]}: boolean)->[{nltk_nouns[0]}]\n")
                    i = i + 1
            else:
                while (i < len(nltk_nouns)):
                    f.write(f"({nltk_nouns[i]})->[{nltk_nouns[0]}]\n")
                    i = i + 1
        # If output is in the token
        if "output" in token_sentence:
            while (i < len(nltk_nouns)):
                f.write(f"{nltk_nouns[0]}->({nltk_nouns[i]})\n")
                i = i + 1
    f.close()


def dynamicPlantumlCode(text):
    doc = sent_tokenize(text)

    f = open(r"/src/uml/d_model_specs.txt", 'w')

    # Needed to state what type of diagram is being constructed (State Diagram)
    f.write("state Diagram {\nhide empty description \n[*]--> Start\n")
    # Iterate sentence-by-sentence
    for sent in doc:
        # Call Tokenize and POS Funtion
        token_sentence, pos_tag_token = tokenAndPOS_Tags(sent)

        # Call Noun Extraction Function
        nltk_nouns = nounExtraction(pos_tag_token)

        # if the sentence include condition and true, construct the
        # sentence: input- current state - transition state
        # code: current state-->transition state:[input]
        if ("condition" in token_sentence) and ("true" in token_sentence) is True:
            f.write(f"{nltk_nouns[1]}-->{nltk_nouns[2]}:[{nltk_nouns[0]}]\n")

        # if the sentence include condition and false, construct the
        # sentence: input- current state - transition state
        # code: current state --> transition state: not[input]
        elif ("condition" in token_sentence) and ("false" in token_sentence):
            f.write(f"{nltk_nouns[1]}-->{nltk_nouns[2]}:not[{nltk_nouns[0]}]\n")

        # if the sentence include variable, construct the
        # sentence: variable name- variable assignment- variable location
        # code: variable location:variable name= variable assignment
        elif "variable" in token_sentence:
            f.write(f"{nltk_nouns[2]}:{nltk_nouns[0]}={nltk_nouns[1]}\n")

        # if the sentence include event, construct the
        # sentence: event name- current state- transition state
        # code: current state-->transition state:event[event name]
        elif "event" in token_sentence:
            f.write(f"{nltk_nouns[1]}-->{nltk_nouns[2]}:event[{nltk_nouns[0]}]\n")

    # needed for creating state diagrams
    f.write("}")
    f.close()


def plantUMLServer(path):
    server = PlantUML(url='http://www.plantuml.com/plantuml/img/',
                      basic_auth={},
                      form_auth={}, http_opts={}, request_opts={})
    server.processes_file(abspath(path))


if __name__ == "__main__":
    # specification text
    static_text = open(r"/src/data/static_text.txt", "r")

    dynamic_text = open(r"/src/data/dynamic_text.txt", "r")

    dynamicPlantumlCode(dynamic_text.read())
    staticPlantumlCode(static_text.read())
    plantUMLServer("/src/uml/d_model_specs.txt")
    plantUMLServer("/src/uml/s_model_specs.txt")
