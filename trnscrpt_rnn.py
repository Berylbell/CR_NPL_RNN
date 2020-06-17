# -*- coding: utf-8 -*-
"""
Created on Sat Jun  6 12:54:53 2020

@author: Berylroll

Clean transcript, seperate speakers and dialogue, train two seperate rnns to 
determine order of talking and then the dialogue of each individual speaker
"""


import tensorflow as tf
import numpy as np
import os
import trnscrptClean as trclean
import pullCRTranscripts as pullTran
import rnn_nlp
import random
import azureml

#Use transcript to train a RNN on the order of the speakers
def run_model_order(speakers):
    #Make vocab 
    vocab_s = sorted(set(speakers))
    
    #set up mapping
    spe2idx = {u:i for i, u in enumerate(vocab_s)}
    #idx2spe = np.array(vocab_s)    
    speak_2_int = np.array([spe2idx[c] for c in speakers])
    #define size of speaker and dataset slices
    seq_length = 100
    speaker_dataset = tf.data.Dataset.from_tensor_slices(speak_2_int)
    
    sequences = speaker_dataset.batch(seq_length+1, drop_remainder=True)
    dataset_s = sequences.map(rnn_nlp.split_input_target)
    # Define Batch Size/ Buffer size
    BATCH_SIZE = 16
    BUFFER_SIZE = 10000
    dataset_s = dataset_s.shuffle(BUFFER_SIZE).batch(BATCH_SIZE, drop_remainder=True)
    
    #Building the Model
    vocab_size_s = len(vocab_s)
    embedding_dim = 256
    rnn_units = 1024
    model_s = rnn_nlp.build_model(vocab_size = len(vocab_s), embedding_dim = embedding_dim, rnn_units = rnn_units, batch_size = BATCH_SIZE)
    #Compile Model
    model_s.compile(optimizer='adam', loss=rnn_nlp.loss)
    
    #Save the Checkpoints
    checkpoint_dir = './training_checkpoints_orderCR'
    checkpoint_prefix = os.path.join(checkpoint_dir, "ckpt_{epoch}")
    checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(
        filepath= checkpoint_prefix, save_weights_only=True)
    
    
    #Run the code with Epochs
    EPOCHS=10
    history = model_s.fit(dataset_s,epochs=EPOCHS, callbacks= [checkpoint_callback])
    
    #tf.train.latest_checkpoint(checkpoint_dir)
    
    #Build the Model
    model_s = rnn_nlp.build_model(vocab_size_s, embedding_dim, rnn_units, batch_size=1)
    model_s.load_weights(tf.train.latest_checkpoint(checkpoint_dir))
    model_s.build(tf.TensorShape([1,None]))
    #return(model_s)
    #return(order)

#Use a Trained RNN to generate an order of speakers 
def build_order(speakers, length=2):
    #Building the Model
    vocab_s = sorted(set(speakers))
    vocab_size_s = len(vocab_s)
    embedding_dim = 256
    rnn_units = 1024
    
    model_s = rnn_nlp.build_model(vocab_size_s, embedding_dim, rnn_units, batch_size=1)
    checkpoint_dir = './training_checkpoints_orderCR'
    model_s.load_weights(tf.train.latest_checkpoint(checkpoint_dir))
    order = rnn_nlp.generate_text(model_s, speakers[3:], speakers, length, returntype='list')
    return(order)

#Generate the script from the trained rnn with given order of speakers
def generateScript (order, speak_text):

    #Make empty string for generated text 
    #Run in the order to generate dialog 
    #Save in a file 
    gen = ''
    count = 0
    gendia = 'PreShow' 
    file = open("genCR.txt","r+")
    file.truncate(0)
    file.close()
    for pers in order:
        length = len(random.choice(speak_text[pers]))
        #print(''.join(speak_text[pers]))
        topic = trclean.pick_topic(gendia,speak_text[pers])
        print(topic)
        gendia = rnn_nlp.prod_text_from_file(''.join(speak_text[pers]), pers, topic, length)
        #print(gendia)
        gen =': '.join([pers, gendia])
        gen = gen + '\n'
        with open("gen2_1.txt", "a") as myfile:
            myfile.write(gen)
        
        count+=1
        if(count>50):
            break
    
#Run TODO: option to download the transcripts, options for generate text, option for filepath for gen
def runRNNTrans ():
    #Choose File Path
    #OPTIONAL PULL TRANSCRIPTS
    #pullTran.pullScripts()
    path_to_file = 'Transcripts\\transcript2_master.txt'
    text = open(path_to_file, 'rb').read().decode(encoding='utf-8')

    #First load text and run transcript clean
    [speakers, dia, speak_text] = trclean.seperate_Chara(text)

    #input('Reached text processing: cont')

    #---------------------------Train a RNN for Each Speaker---------------------------
    good_list = ["MATT", "MARISHA", "LAURA", "LIAM", "SAM", "ASHLEY", "TRAVIS", "TALIESIN", "ALL", "KHARY", "MARK","SUMALEE", "DEBORAH", "CHRIS", "MICA", "OTHER"]
    #rnn_nlp.run_rnn_nlp(text,"test", 1)
    def train_speakers(speak_text):
        for speak in speak_text:
            if (speak in good_list):
                #print(speak_text[speak])
                print(speak)
                #print(''.join(speak_text[speak]))
                #input('running rnn. cont:')
                if(len(''.join(speak_text[speak]))>=400):
                    rnn_nlp.run_rnn_nlp(''.join(speak_text[speak]), speak, 3)
        
    train_speakers(speak_text)
    #---------------------------Learn the Dialogue Order---------------------------
    run_model_order(speakers)
    order = build_order(speakers)

    #Options to Shorten the order and options to use and test order
    #order = order[10:]
    #order = ["OTHER", "MATT", "LAURA", "SAM", "LIAM", "TRAVIS", "TALIESIN", "MARISHA"]

    #-----------------------Generate Script-----------------------------------------
    generateScript(order, speak_text)

runRNNTrans()