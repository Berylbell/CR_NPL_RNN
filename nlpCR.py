# -*- coding: utf-8 -*-
"""
Created on Wed Jun  3 21:43:58 2020

@author: Berylroll
CR transcript from stackabuse
"""

import numpy
import sys
import tensorflow as tf
import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, LSTM
from tensorflow.keras import utils
from tensorflow.keras.callbacks import ModelCheckpoint

nltk.download('stopwords')
#Choose our training text
#In this case we are using the transcript from 2x01 CR
path_to_file = 'transcript2_1.txt'
file = open(path_to_file, 'rb').read().decode(encoding='utf-8')

#First we preprocess out text. This involves tokenizing, removing stopwords, lowercasing everything

def tokenize_words(input):
    
    #Lowercase Everything
    input = input.lower()
    
    #Tokenize input
    tokenizer = RegexpTokenizer(r'w+')
    tokens = tokenizer.tokenize(input)
    
    #Search for stopwords and remove
    filtered = filter( lambda token: token not in stopwords.words('english'), tokens)
    
    #Return Filtered Content
    return " ".join(filtered)
    
#call it on our inout
processed_inputs = tokenize_words(file)

#create our dictionary
chars = sorted(list(set(processed_inputs)))
char_to_num = dict((c,i) for i, c in enumerate(chars))

#create vocad and input lens
input_len = len(processed_inputs)
vocab_len = len(chars)

print("Total chars: ", input_len)
print("Total vocab: ", vocab_len)


#def seq len and x,y data
seq_length = 100
x_data = []
y_data = []

#fill x,y
for i in range(0, input_len - seq_length, 1):
    #using sequence length, define in and out sequences
    in_seq = processed_inputs[i:i +seq_length]
    out_seq = processed_inputs[i+ seq_length]
    x_data.append([char_to_num[char] for char in in_seq])
    y_data.append(char_to_num[out_seq])
    
n_patterns = len(x_data)
print ("total patterns: ", n_patterns)

#convert into a numpy array between 0-1 which the sigmoid fn can use
X = numpy.reshape(x_data, (n_patterns, seq_length,1))
X = X/float(vocab_len)

#hot-one encoding
y = utils.to_categorical(y_data)

#Now define our nn model

model = Sequential()
model.add(LSTM(256, input_shape=(X.shape[1], X.shape[2]), return_sequences=True))
model.add(Dropout(0.2))
model.add(LSTM(256, return_sequences=True))
model.add(Dropout(0.2))
model.add(LSTM(128))
model.add(Dropout(0.2))
model.add(Dense(y.shape[1], activation='softmax'))
model.compile(loss='categorical_crossentropy', optimizer='adam')

#Now we save the weights for the future
filepath = "model_weights_saved_CR.hdf5"
checkpoint = ModelCheckpoint(filepath, monitor='loss', verbose=1, save_best_only=True, mode='min')
desired_callbacks = [checkpoint]

#Finally we train it
model.fit(X,y, epochs=20, batch_size=16, callbacks=desired_callbacks)

#Load the final weights
model.load_weights(filepath)
model.compile(loss='categorical_crossentropy', optimizer='adam')

#Convert back to char
num_to_char = dict((i,c) for i,c in enumerate(chars))

#Give it a random seed 
start = numpy.random.randint(0, len(x_data) - 1)
pattern = x_data[start]
print("Random Seed:")
print("\"", ''.join([num_to_char[value] for value in pattern]), "\"")

for i in range(1000):
    x = numpy.reshape(pattern,(1,len(pattern),1))
    x = x/ float(vocab_len)
    prediction = model.predict(x,verbose=0)
    index = numpy.argmax(prediction)
    result = num_to_char[index]
    seq_in = [num_to_char[value] for value in pattern]
    sys.stdout.write(result)
    pattern.append(index)
    pattern = pattern[1:len(pattern)]
    
