# -*- coding: utf-8 -*-
"""
Created on Tue Jun  2 19:31:49 2020

@author: Berylroll

Using the Tensorflow tutorials and twint to download matthew mercer's tweets and 
train a 3 layer RNN on them to produce Matt Style Tweets
"""
import functools
import tensorflow as tf
import pandas as pd
import numpy as np
import os
import time
import twint
import twitterclean
import nest_asyncio
import time

#tf.enable_eager_execution()
# print(tf.executing_eagerly())
# nest_asyncio.apply()
# #dowload tweets
# c = twint.Config()
# c.Username = "matthewmercer"
# c.Store_csv = True
# c.Limit = 10000
# c.Output = "matt.csv"
# c.Hide_output= True

# start = time.time()
# #os.remove("matt.csv")
# #twint.run.Search(c)
# end = time.time()
# print(end - start)

#print("finished download")
#read tweets and clean the tweets
#mTweet = pd.read_csv('matt.csv')
#mTweet['cleaned_tweets']=mTweet['tweet'].apply(lambda x: twitterclean.process_text(x))
#mTweet['tweet']=mTweet['tweet'].apply(lambda x: twitterclean.remove_content(x))

#print("finished clean")
#Save the combined cleaned tweets to txt file
#print(mTweet['cleaned_tweets'].head())
#max_tweet = max(mTweet['cleaned_tweets'], key=len)
#text = mTweet['cleaned_tweets'].str.cat(sep='\n \n ')
path_to_file = 'harryfic.txt'
text = open(path_to_file, 'rb').read().decode(encoding='utf-8')
#np.savetxt(r'C:\Users\Admin\Desktop\Side\pythonside\matt.txt', mTweet['cleaned_tweets'].values, fmt='%s \n')
#print("finished save")


#prep vocab
vocab = sorted(set(text))

print(vocab)

#set up mapping
char2idx = {u:i for i, u in enumerate(vocab)}
idx2char = np.array(vocab)    
text_2_int = np.array([char2idx[c] for c in text])

#define size of tweet and dataset slices
seq_length = 100 #len(max_tweet) #100
examples_per_epoch = len(text)
char_dataset = tf.data.Dataset.from_tensor_slices(text_2_int)

sequences = char_dataset.batch(seq_length+1, drop_remainder=True)

def split_input_target(chunk):
    input_text = chunk[:-1]
    target_text = chunk[1:]
    return input_text, target_text

dataset = sequences.map(split_input_target)
print(dataset)

# Define Batch Size/ Buffer size
BATCH_SIZE = 16
BUFFER_SIZE = 10000
dataset = dataset.shuffle(BUFFER_SIZE).batch(BATCH_SIZE, drop_remainder=True)



#Building the Model

vocab_size = len(vocab)
embedding_dim = 256
rnn_units = 1024

def build_model(vocab_size, embedding_dim, rnn_units, batch_size):
    model = tf.keras.Sequential([tf.keras.layers.Embedding(vocab_size, embedding_dim, batch_input_shape= [batch_size, None]),
                                 tf.keras.layers.GRU(rnn_units, return_sequences = True, stateful = True, recurrent_initializer = 'glorot_uniform'),
                                 tf.keras.layers.Dense(vocab_size)])
    return model

model = build_model(vocab_size = len(vocab), embedding_dim = embedding_dim, rnn_units = rnn_units, batch_size = BATCH_SIZE)

print("model Built")
#Testing Model
for input_example_batch, target_example_batch in dataset.take(1):
  example_batch_predictions = model(input_example_batch)
  print(example_batch_predictions.shape, "# (batch_size, sequence_length, vocab_size)")

#Print the summary and the examples 
print(model.summary())

sampled_indices = tf.random.categorical(example_batch_predictions[0], num_samples=1)
sampled_indices = tf.squeeze(sampled_indices, axis=-1).numpy()

print(sampled_indices)

print("Input: \n", repr("".join(idx2char[input_example_batch[0]])))
print()
print("Next Char Predictions: \n", repr("".join(idx2char[sampled_indices ])))

#Define the loss
def loss(labels, logits):
    return tf.keras.losses.sparse_categorical_crossentropy(labels, logits, from_logits=True)

example_batch_loss = loss(target_example_batch, example_batch_predictions)
print("Prediction shape: ", example_batch_predictions.shape, " # (batch_size, sequence_length, vocab_size)")
print("scalar_loss:      ", example_batch_loss.numpy().mean())

#Compile the model with the loss fn
model.compile(optimizer='adam', loss=loss)

#Save the Checkpoints
checkpoint_dir = './training_checkpoints_harryfic'
checkpoint_prefix = os.path.join(checkpoint_dir, "ckpt_{epoch}")
checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(
    filepath= checkpoint_prefix, save_weights_only=True)


#Run the code with Epochs
EPOCHS=40
history = model.fit(dataset,epochs=EPOCHS, callbacks= [checkpoint_callback])

tf.train.latest_checkpoint(checkpoint_dir)

#Build the Model
model = build_model(vocab_size, embedding_dim, rnn_units, batch_size=1)
model.load_weights(tf.train.latest_checkpoint(checkpoint_dir))
model.build(tf.TensorShape([1,None]))

print(model.summary())

#Generate the Text
def generate_text(model, start_string):
    #number of characters to generate
    num_generate = 1000
    #converst string to num
    input_eval = [char2idx[s] for s in start_string]
    input_eval = tf.expand_dims(input_eval,0)
    text_generated = []
    
    #Define Temp: high temp= chaos, low temp = predict
    temperature = 0.9
    
    #batch
    model.reset_states()
    
    for i in range(num_generate):
        predictions = model(input_eval)
        
        #remove the batch dim
        predictions = tf.squeeze(predictions, 0)
        
        #Use categorical dis to predict char by model
        predictions = predictions/temperature
        predicted_id = tf.random.categorical(predictions, num_samples=1)[-1,0].numpy()
        
        #pass predicted character to model along w state
        
        input_eval = tf.expand_dims([predicted_id], 0 )
        text_generated.append(idx2char[predicted_id])
        
    return(start_string + ''.join(text_generated))

print(generate_text(model,start_string=u"Harry "))