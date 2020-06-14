# -*- coding: utf-8 -*-
"""
Created on Tue Jun  2 19:31:49 2020

@author: Berylroll

Using the Tensorflow tutorials and twint to download matthew mercer's tweets and 
train a 3 layer RNN on them to produce Matt Style Tweets
"""

import tensorflow as tf
import numpy as np
import os

def split_input_target(chunk):
    input_text = chunk[:-1]
    target_text = chunk[1:]
    return input_text, target_text


def build_model(vocab_size, embedding_dim, rnn_units, batch_size):
    model = tf.keras.Sequential([tf.keras.layers.Embedding(vocab_size, embedding_dim, batch_input_shape= [batch_size, None]),
                                 tf.keras.layers.GRU(rnn_units, return_sequences = True, stateful = True, recurrent_initializer = 'glorot_uniform'),
                                 tf.keras.layers.Dense(vocab_size)])
    return model

#Define the loss
def loss(labels, logits):
    return tf.keras.losses.sparse_categorical_crossentropy(labels, logits, from_logits=True)


#Generate the Text
def generate_text(model, start_string, text, num_generate=100, temperature =1, returntype ='none'):
    
    vocab = sorted(set(text))
    #converst string to num
    char2idx = {u:i for i, u in enumerate(vocab)}
    idx2char = np.array(vocab)    
    #text_2_int = np.array([char2idx[c] for c in text])
    
    input_eval = [char2idx[s] for s in start_string]
    input_eval = tf.expand_dims(input_eval,0)
    text_generated = []
 
    
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
    
    if(returntype == 'str'):
        return(start_string + ''.join(text_generated))
    elif(returntype == 'list'):
        return(start_string + text_generated)
    else:
        return(''.join(text_generated))
        
def run_rnn_nlp (text, suffix='suffix', EPOCHS =3):
    #Make vocab 
    vocab = sorted(set(text))
    
    print(vocab)
    #set up mapping
    char2idx = {u:i for i, u in enumerate(vocab)}
    #char2spe = np.array(vocab)    
    text_2_int = np.array([char2idx[c] for c in text])
    
    #define size of speaker and dataset slices
    seq_length = 100#int(len(text)/20)
    print(seq_length)
    #input('cont')
    speaker_dataset = tf.data.Dataset.from_tensor_slices(text_2_int)
    
    sequences = speaker_dataset.batch(seq_length+1, drop_remainder=True)
    dataset = sequences.map(split_input_target)
    print(dataset)
    
    # Define Batch Size/ Buffer size
    BATCH_SIZE = 4
    BUFFER_SIZE = 10000
    dataset = dataset.shuffle(BUFFER_SIZE).batch(BATCH_SIZE, drop_remainder=True)
    
    
    #Building the Model
    vocab_size_s = len(vocab)
    embedding_dim = 256
    rnn_units = 1024
    model = build_model(vocab_size = len(vocab), embedding_dim = embedding_dim, rnn_units = rnn_units, batch_size = BATCH_SIZE)
    
    #Compile Model
    model.compile(optimizer='adam', loss=loss)
    
    #Save the Checkpoints
    checkpoint_dir = './training_checkpoints_'+suffix
    checkpoint_prefix = os.path.join(checkpoint_dir, "ckpt_{epoch}")
    checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(
        filepath= checkpoint_prefix, save_weights_only=True)
    
    
    #Run the code with Epochs
    history = model.fit(dataset,epochs=EPOCHS, callbacks= [checkpoint_callback])
    tf.train.latest_checkpoint(checkpoint_dir)
    
    #Build the Model
    model = build_model(vocab_size_s, embedding_dim, rnn_units, batch_size=1)
    model.load_weights(tf.train.latest_checkpoint(checkpoint_dir))
    model.build(tf.TensorShape([1,None]))
    
    
def prod_text_from_file(text, suffix='suffix', start_string='', length=100):
    
    vocab = sorted(set(text))
    
    vocab_size = len(vocab)
    embedding_dim = 256
    rnn_units = 1024
    
    checkpoint_dir = './training_checkpoints_'+suffix
    
    model = build_model(vocab_size, embedding_dim, rnn_units, batch_size=1)
    model.load_weights(tf.train.latest_checkpoint(checkpoint_dir))
    model.build(tf.TensorShape([1,None]))
    
    #print(model.summary())
    gen= generate_text(model,start_string, text, length, 1, 'str')
    return gen
    