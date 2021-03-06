import torch
import numpy as np
import pandas as pd
import math
import random
from tqdm import tqdm
import pickle

#hidden dimensionality of the word embeddings
N = 300

#Context Size
C = 5

#Learning Rate for SGD
alpha = 0.001

#No. of Negative Samples
K = 5

#Number of Epochs
num_epochs = 3

"""
Importing Vocabulary from pre-processing.py
"""

vocabulary_file = open("Pickle/vocabulary_file.pkl",'rb')
VOCABULARY = pickle.load(vocabulary_file)
vocabulary_file.close()


VOCABULARY_SIZE = len(VOCABULARY)

"""
Importing Tokenized Corpus from pre-processing.py
"""

token_vocabulary_file = open("Pickle/token_vocabulary_file.pkl",'rb')
tokens_vocab = pickle.load(token_vocabulary_file)
token_vocabulary_file.close()

"""
Importing Training Data from pre-processing.py
"""
train_data_file = open("Pickle/train_data_file.pkl",'rb')
train_data = pickle.load(train_data_file)
train_data_file.close()

"""
Importing Unigram Ratios from pre-processing.py
"""
unigram_file = open("Pickle/unigram_ratios_file.pkl",'rb')
UNIGRAM_RATIOS = pickle.load(unigram_file)
unigram_file.close()

"""
Function to generate One Hot Encoding
"""

def generateOneHotEncoding(word):
    one_hot_encoded_vector = torch.zeros(VOCABULARY_SIZE)
    one_hot_encoded_vector[VOCABULARY[word]] = 1
    return one_hot_encoded_vector

"""
Function to generate Noise Distribution (Needs to be executed exactly once!)
Input : Corpus Vocabulary
Output : Noise distribution for Negative Sampling
"""
def generateNoiseDist():
    #Read this variable from a txt file here
    unigram_counts = len(tokens_vocab)*UNIGRAM_RATIOS

    unigram_counts = unigram_counts ** 0.75
    sum_counts = sum(unigram_counts)

    noise_distribution = unigram_counts/sum_counts

    return noise_distribution

"""Class implementing the Skip-Gram Model from scratch"""

class SkipGram():
    """
    Constructor initializes input and output weight matrices
    """
    def __init__(self):
        self.W_in = ((-2/math.sqrt(N))*torch.rand(VOCABULARY_SIZE,N) + 1/math.sqrt(N))
        self.W_out = ((-2/math.sqrt(N))*torch.rand(N,VOCABULARY_SIZE) + 1/math.sqrt(N))

    """
    Function to perform a forward pass through the Skip Gram
    Input : Current Instance of Class
    Output : C probability distributions, each representing a context
    """
    def forward(self, inp_index):
        self.h = self.W_in[inp_index]
        self.out = torch.matmul(torch.transpose(self.W_out, 0 ,1), self.h)
        return self.out

    """
    Function to compute gradients wrt input & output vectors and the hidden layer output
    Input : Noise Distribution, input string, one hot encoded input, context string
    Output : All the gradients
    """
    def gradients(self, noise_distribution, inp_index, context):

        self.inp_grad = torch.zeros(N)
        
        for id in range(len(context)):

            #performing the forward pass through the Skip Gram Network

            self.forward(inp_index)

            #sampling K negative samples from the Noise Distribution
        
            D_dash = random.choices(list(VOCABULARY.keys()), noise_distribution, k = K)

            #updating output vectors of negative samples

            for i in range(K):
                self.W_out[:,VOCABULARY[D_dash[i]]] -= alpha * torch.sigmoid(torch.dot(self.W_out[:,VOCABULARY[D_dash[i]]], self.h))*self.h
                
            #updating output vector of the positive sample (our context word)

            self.W_out[:,context[id]] -= alpha * (torch.sigmoid(torch.dot(self.W_out[:,context[id]], self.h)) - 1)*self.h

            #computing gradient for input vector

            for i in range(K):
                self.inp_grad += torch.sigmoid(torch.dot(self.W_out[:,VOCABULARY[D_dash[i]]], self.h))* self.W_out[:,VOCABULARY[D_dash[i]]]
            
            self.inp_grad += (torch.sigmoid(torch.dot(self.W_out[:,context[id]], self.h)) - 1)*self.W_out[:,context[id]] 

        #updating the input vector after all contexts are done
        self.W_in[inp_index] -= alpha * self.inp_grad


"""
Format of each training instance
(input_word, list containing all context words in the window)
"""

#Generates the special unigram frequencies from which to negative sample from
noise_distribution = torch.Tensor(generateNoiseDist())

skip_gram = SkipGram()

for epoch in range(num_epochs):
    for idx, (inp, context) in enumerate(tqdm(train_data)):

        inp_index = VOCABULARY[inp]

        context = torch.tensor([VOCABULARY[c] for c in context])

        skip_gram.gradients(noise_distribution, inp_index, context)


#Writing the Matrix of i/p word vectors to a pickle file

print(skip_gram.W_in)

print(skip_gram.W_in.shape)

word_embeddings_file = open("Pickle/word_embeddings_file.pkl",'wb')
pickle.dump(skip_gram.W_in, word_embeddings_file)
word_embeddings_file.close()