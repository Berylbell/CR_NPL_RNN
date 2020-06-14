# -*- coding: utf-8 -*-
"""
Created on Sat Jun  6 11:54:16 2020

@author: Berylroll

Clean transcripts
"""
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize 
from nltk.stem import PorterStemmer
import random
import re

path_to_file = 'Transcripts\\transcript2_master.txt'
text = open(path_to_file, 'rb').read().decode(encoding='utf-8')
#re.sub(r'(\r\n){2,}','\r\n', text)

def seperate_Chara(text):
    #TODO: LIAM\xa0  also MATT sometimes????
    lines = text.split('\n')
    speaker = []
    dia = []
    speak_text = dict()
    
    for line in lines:
        
        #TODO: properly find the seperators for when multiple people are talking and
        #either assign the text to the individuals, or regularize it. 
        line = line.replace('\r', '')
        if(line.count('\r')>0):
            print(line)
        splits = line.count(':')
        txtsplit = line.split(':')
        if(splits == 1):
            #preprocess when there are multiple speakers
            spk = txtsplit[0].replace(' and ', ' ')
            spk = spk.replace(' ', ',')
            spk = re.sub(",+", ",", spk)
            spk = spk.upper()
            speaker.append(spk)

            dia.append(txtsplit[1])            
            speak_text.setdefault(spk, [])
            speak_text[spk].append(txtsplit[1])
            #speak_text[txtsplit[0]] = txtsplit[1]
            
        elif (splits == 0):
            if(not( line.isspace() or line =='')):
                #Use to check for lines that are continuations of prev
                #print(line)
                if(line.count('.')==0):
                    speaker.append('OTHER')
                    dia.append(line)
                    speak_text.setdefault('OTHER',[])
                    speak_text['OTHER'].append(line)
                    #speak_text['OTHER'] =  line
                else:
                    dia[-1]= dia[-1] + line
                    #speak_text.setdefault('OTHER',[])
                    speak_text[speaker[-1]].append(line)
                    #speak_text['OTHER'] =  line
        else:
            #preprocess when there are multiple speakers
            spk = txtsplit[0].replace(' and ', ' ')
            spk = spk.replace(' ', ',')
            spk = re.sub(",+", ",", spk)
            spk = spk.upper()
            speaker.append(spk)

            speaker.append(spk)
            dia.append(txtsplit[1])
            speak_text.setdefault(spk, [])
            speak_text[spk].append(txtsplit[1])
        
        #if(not speaker in ['MATT', 'MARISHA', 'SAM','TRAVIS', 'LIAM', 'LAURA','TALIESIN', 'ASHLEY','OTHER']):
         #   print(speaker[-1])
         #   input('count.')
        # print(line)
        # print(txtsplit)
        # print(speak_text)
        # input("cont")
    #print(speak_text['ASHLEY'])

    
    return [speaker, dia, speak_text]
        
   
def pick_topic(prevtext, currentvocab):

    vocab = set(list(''.join(currentvocab)))
    #vocab =set(vocab)       
    set(stopwords.words('english'))
    stop_words = set(stopwords.words('english')) 
    prevtext = re.sub('[^A-Za-z]', ' ', prevtext)
    
    filtered_sentence = [] 
    word_tokens = word_tokenize(prevtext) 
    for w in word_tokens: 
        if w not in stop_words: 
            filtered_sentence.append(w)       
    
    if(not filtered_sentence):
        filtered_sentence = prevtext
    
    choice = random.choice(filtered_sentence)
    count= 0 
    while (not vocab.issuperset(choice)):
            choice = random.choice(filtered_sentence)
            print(count)
            count=+1
            if count>100:
                break
        
    return choice
                                        
[speaker, dia, speak_text] = seperate_Chara(text)

print(set(speaker))

# for speak in speak_text:
#     #rnn_nlp.run_rnn_nlp(speak_text[speak], speak)
#     print(speak)
#     print(speak_text[speak])
#     print("------------------------------------------------------------------")
#     input("cont")
    