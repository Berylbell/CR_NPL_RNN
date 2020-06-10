# -*- coding: utf-8 -*-
"""
Created on Fri Jun  5 19:13:29 2020

@author: Berylroll

reload model and create text from given weights
"""

import tensorflow as tf
import rnn_nlp

path_to_file = 'transcript2_1.txt'
text = open(path_to_file, 'rb').read().decode(encoding='utf-8')

vocab = sorted(set(text))

vocab_size = len(vocab)
embedding_dim = 256
rnn_units = 1024
BATCH_SIZE = 16

checkpoint_dir = './training_checkpoints_trscpt'

model = rnn_nlp.build_model(vocab_size, embedding_dim, rnn_units, batch_size=1)
model.load_weights(tf.train.latest_checkpoint(checkpoint_dir))
model.build(tf.TensorShape([1,None]))

print(model.summary())


print(rnn_nlp.generate_text(model,u"LAURA: ", text, 4000))

