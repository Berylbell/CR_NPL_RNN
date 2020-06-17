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

#From the CR transcripts, create a dictionary of the speakers and a string of their full dialog
#as well as lists representing the order of the speakers and the order of the dialog
#the seperator between speaker and dialog is the ":". This processor does its best to work on this 
#principal and account for special cases. 
def seperate_Chara(text):
    lines = text.split('\n')
    speaker = []
    dia = []
    speak_text = dict()    
    for line in lines:
        
        #remove the newlines
        line = line.replace('\r', '')

        #Treat some of the badtype lines
        if( "And my stumble forward going" in line):
            line = "MARISHA: "+line
        elif("slightly better:" in line):
            line = line.replace(":", "")
        elif("patrolling and keeping an eye." in line):
            line = "MATT: "+line
        elif("little wire and says:" in line):
            line = "LIAM: "+line
        elif("their hands like:" in line):
            line = "MATT: "+line 
        elif("keyword: beard, B-E-A-R-D, beard." in line):
            line = line.replace(":", "")
        elif("a semblance of a softer floor" in line):
            line = "MATT: "+line
        elif("Mighty Nein here in Xhorhas having allied themselves for the time being with" in line):
            line = "MATT: "+line
        elif("Marion: “Of course, of course, trust me" in line):
            line = line.replace(":", ",")

        #If its just a time stamp, remove it 
        line = re.sub('^\d+:\d+:\d+\s+-\s+\d+:\d+:\d+', '', line)
        #If its a time, remove the semicolon
        line = re.sub('(?<=\d):(?=\d+)', '', line)
        splits = line.count(':')
        txtsplit = line.split(':', 1)
        if(splits >= 1):
            #isolate spakers
            spk = txtsplit[0]

            #find the action bf : and replace it 
            action = re.findall('\([^()]*\)',spk)
            spk = re.sub('\([^()]*\)','', spk)

            #preprocess for when there are multiple speakers
            spk = spk.replace(' and ', ' ')
            spk = spk.replace(' an ', ' ')
            di = '('+' '.join(action) + ') '+ txtsplit[1] 
            spk = spk.strip()
            spk = spk.replace(' ', ',')
            spk = re.sub(",+", ",", spk)
            spk = spk.upper()
        
            #if more than one speaker, add text to all speakers, then 
            #add together to dia
            #otherwise, just add normally
            if(spk.count(',') >= 1):
                spk = spk.split(',')
                di = '(together) '+di
                for i in spk:
                    speaker.append(i)
                    dia.append(di)            
                    speak_text.setdefault(i, [])
                    speak_text[i].append(di)
                    # if (not i in good_list):
                    #     print(line)
                    #     print(i)
                    #     input('cont')

            else:
                speaker.append(spk)
                dia.append(di)            
                speak_text.setdefault(spk, [])
                speak_text[spk].append(di)
                # if(not spk in good_list):
                #     print(line)
                #     print(i)
                #     input('cont')

        else:
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
        # else:
        #     spk = txtsplit[0].replace(' and ', ' ')
        #     di = txtsplit[1]
        #     spk = spk.strip()
        #     spk = spk.replace(' ', ',')
        #     spk = re.sub(",+", ",", spk)
        #     spk = spk.upper()

        #     #if more than one speaker, add text to all speakers, then 
        #     #add together to dia
        #     #otherwise, just add normally
        #     if(False):#(spk.count(',') > 1):
        #         spk = spk.split(',')
        #         di = '(together) '+di
        #         for i in spk:
        #             speaker.append(i)
        #             dia.append(di)            
        #             speak_text.setdefault(i, [])
        #             speak_text[i].append(di)

        #     else:
        #         speaker.append(spk)
        #         dia.append(di)            
        #         speak_text.setdefault(spk, [])
        #         speak_text[spk].append(di)
    
    return [speaker, dia, speak_text]
        

#This function takes the previous generated text and picks a topic from it which is within the 
#vocabulary of the current speaker
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

# path_to_file = 'Transcripts\\transcript2_master.txt'
# text = open(path_to_file, 'rb').read().decode(encoding='utf-8')                                    
# [speaker, dia, speak_text] = seperate_Chara(text)
# for spk in set(speaker):
#     print(spk)
