import re
import math
import pickle
import tqdm

from loguru import logger

import numpy as np
import pandas as pd

import nltk
from nltk.corpus import wordnet
from nltk.corpus import stopwords

import torch

NUM_SAMPLES = 0
DELETE_THRESHOLD = 0.4

SENTENCES_1 = []
SENTENCES_2 = []
SIMILARITY_SCORES = []
STOPWORDS = []

"""
Function to tokenize strings
Input: Text
Output: Tokenized version of string, Corpus Size
"""
def generateTokens(text):
    pattern = re.compile(r'[A-Za-z]+[\w^\']*|[\w^\']*[A-Za-z]+[\w^\']*')
    return pattern.findall(text.lower())

"""
Function to parse data from SICK dataset
Input: Lines read from file
Output: Sentence 1, Sentence 2, Similarity Scores
"""
def parseData(lines):
    sentences_1 = []
    sentences_2 = []
    similarity_scores = []

    for line in lines:
        tab_count = 0
        s1 = ""
        s2 = ""
        score = ""
        s1_stop = False
        s2_stop = False

        for char in line:
            if(char == '\t'):
                tab_count += 1

            if(tab_count == 2 and char=='\t' and s1_stop == False):
                s1 += ". "
            elif(tab_count == 3 and char=='\t' and s2_stop == False):
                s2 += ". "

            if(tab_count == 1 and char!='\t'):
                s1 += str(char)
                if(char == '.'):
                    s1_stop = True
            elif(tab_count == 2 and char!='\t'):
                s2 += str(char)
                if(char == '.'):
                    s2_stop = True
            elif(tab_count == 4 and char!='\t'):
                score += str(char)
        
        sentences_1.append(s1)
        sentences_2.append(s2)
        similarity_scores.append(score)

    sentences_1.pop(0)
    sentences_2.pop(0)
    similarity_scores.pop(0)
    
    return sentences_1, sentences_2, similarity_scores

"""
Function to generate synonyms of a word from WordNet
Input: Word
Output: List of synonyms and similarity scores from WordNet
"""
def generateSynonyms(word):
    if(len(wordnet.synsets(word)) != 0):
        string = wordnet.synsets(word)[0]
    synonyms = []
    for synonym in wordnet.synsets(word):
        for lemma in synonym.lemmas():
            if(lemma.name().lower() != word.lower() and lemma.name().lower() not in synonyms):
                synonyms.append(tuple((lemma.name().replace("_", " ").replace("-", " ").lower(),string.wup_similarity(synonym))))
    
    return synonyms

"""
Function to randomly delete a stop word from a sentence
Input: Sentence
Output: Sentence with a stop word deleted
"""
def deleteRandomStopWord(sentence):
    tokens = generateTokens(sentence)
    probabilities = np.ones(len(tokens))

    for i,token in enumerate(tokens):
        if token in STOPWORDS:
            probabilities[i] = np.random.uniform(0,1)
    
    words = []
    for i,token in enumerate(tokens):
        if i != np.argmin(probabilities):
            words.append(token)
    
    new_sentence = " ".join(words)
    new_sentence += "."
    return new_sentence

"""
Function to randomly insert a stop word in a sentence
Input: Sentence
Output: Sentence with a stop word inserted
"""
def insertRandomStopWord(sentence):
    tokens = generateTokens(sentence)
    probabilities = np.ones(len(STOPWORDS))

    for i,word in enumerate(STOPWORDS):
        probabilities[i] = np.random.uniform(0,1)

    stop_word = STOPWORDS[np.argmax(probabilities)]
    position = np.random.randint(0,len(tokens))
    words = []
    for i,token in enumerate(tokens):
        if i == position:
            words.append(stop_word)
            words.append(token)
        else:
            words.append(token)
    
    new_sentence = " ".join(words)
    new_sentence += "."
    return new_sentence

file = open("Data/SICK.txt", "r")
lines = file.readlines()
file.close()

STOPWORDS = stopwords.words('english')
SENTENCES_1, SENTENCES_2, SIMILARITY_SCORES = parseData(lines)

NUM_SAMPLES = len(SENTENCES_1)

"""
Generating non-augmented Sick Dataset
"""
# file = open("Data/data_sick.txt", "w")
# for i in range(0,NUM_SAMPLES):
#     line = SENTENCES_1[i] + "\t" + SENTENCES_2[i] + "\t" + str(SIMILARITY_SCORES[i]) + "\n"
#     file.write(line.lower())
# file.close()

"""
Generating non-augmented Sick Dataset (Training)
"""
# file = open("Data/data_sick_train.txt", "w")
# for i in range(0,int(NUM_SAMPLES/2)):
#     line = SENTENCES_1[i] + "\t" + SENTENCES_2[i] + "\t" + str(SIMILARITY_SCORES[i]) + "\n"
#     file.write(line.lower())
# file.close()

"""
Generating non-augmented Sick Dataset (Test)
"""
# file = open("Data/data_sick_test.txt", "w")
# for i in range(int(NUM_SAMPLES/2),NUM_SAMPLES):
#     line = SENTENCES_1[i] + "\t" + SENTENCES_2[i] + "\t" + str(SIMILARITY_SCORES[i]) + "\n"
#     file.write(line.lower())
# file.close()

"""
Generating Sick Dataset (Training) augmented using Random Stop Word Deletion
"""
# file = open("Data/data_random_deletion.txt", "w")
# for i in range(0,int(NUM_SAMPLES/2)):
#     line = SENTENCES_1[i] + "\t" + SENTENCES_2[i] + "\t" + str(SIMILARITY_SCORES[i]) + "\n"
#     file.write(line.lower())

#     new_sentence = deleteRandomStopWord(SENTENCES_1[i])
#     line = new_sentence + "\t" + SENTENCES_2[i] + "\t" + str(SIMILARITY_SCORES[i]) + "\n"
#     file.write(line.lower())

#     new_sentence = deleteRandomStopWord(SENTENCES_2[i])
#     line = SENTENCES_1[i] + "\t" + new_sentence + "\t" + str(SIMILARITY_SCORES[i]) + "\n"
#     file.write(line.lower())

#     new_sentence_1 = deleteRandomStopWord(SENTENCES_1[i])
#     new_sentence_2 = deleteRandomStopWord(SENTENCES_2[i])
#     line = new_sentence_1 + "\t" + new_sentence_2 + "\t" + str(SIMILARITY_SCORES[i]) + "\n"
#     file.write(line.lower())
# file.close()

"""
Generating Sick Dataset (Training) augmented using Random Stop Word Insertion
"""
# file = open("Data/data_random_insertion.txt", "w")
# for i in range(0,int(NUM_SAMPLES/2)):
#     line = SENTENCES_1[i] + "\t" + SENTENCES_2[i] + "\t" + str(SIMILARITY_SCORES[i]) + "\n"
#     file.write(line.lower())

#     new_sentence = insertRandomStopWord(SENTENCES_1[i])
#     line = new_sentence + "\t" + SENTENCES_2[i] + "\t" + str(SIMILARITY_SCORES[i]) + "\n"
#     file.write(line.lower())

#     new_sentence = insertRandomStopWord(SENTENCES_2[i])
#     line = SENTENCES_1[i] + "\t" + new_sentence + "\t" + str(SIMILARITY_SCORES[i]) + "\n"
#     file.write(line.lower())

#     new_sentence_1 = insertRandomStopWord(SENTENCES_1[i])
#     new_sentence_2 = insertRandomStopWord(SENTENCES_2[i])
#     line = new_sentence_1 + "\t" + new_sentence_2 + "\t" + str(SIMILARITY_SCORES[i]) + "\n"
#     file.write(line.lower())
# file.close()