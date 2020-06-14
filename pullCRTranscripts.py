# -*- coding: utf-8 -*-
"""
Created on Sat Jun  6 19:06:47 2020

@author: berylroll

script to download transcripts from CR wiki page
"""

import requests
import re
import io
import os 
from bs4 import BeautifulSoup
import trnscrptClean as tc

def get_page (url= 'https://criticalrole.fandom.com/wiki/Transcripts'):
    #download a webpage and preprocess the html
    res = requests.get(url)
    html_page = res.content
    soup = BeautifulSoup(html_page, 'html.parser')
    text = soup.find_all(text=True)
    output = ''
    blacklist = [
    	'[document]',
    	'noscript',
    	'header',
    	'html',
    	'meta',
    	'head', 
    	'input',
    	'script',
    	# there may be more elements you don't want, such as "style", etc.
    ]
    
    for t in text:
    	if t.parent.name not in blacklist:
    		output += '{} '.format(t)
    
    return output

def get_eps_names(main_page):
    #finds all the ep names from season 2 and returns them in a list
    main_page = main_page[main_page.find("Campaign 2: The Mighty Nein Edit")+1:main_page.find("Specials Edit")]
    names = re.findall(r'\"(.+?)\"',main_page)
    return names
    

def download_all(names):
    #make urls for all eps transcripts
    wiki= 'https://criticalrole.fandom.com/wiki/'
    tran= '/Transcript'
    try:
        os.remove("Transcripts\\transcript2_master.txt")
    except:
        print("Masterfile didnt exist")

    for i in range(0,len(names)):
        
        #Special Cases
        if (names[i] == ' Xhorhas '):
            names[i] = ' Xhorhas (episode) '
        if (names[i] == ' O Captain, Who\'s Captain? '):
            names[i] = ' O_Captain,_Who%27s_Captain%3F '
            
        #replace spaces with _ and take out first and last spaces
        #print(names[i])
        url = names[i].replace(' ', '_')[1:-1]        
        url = wiki + url +tran    
        
        #get raw input
        outputin = get_page(url)
        #write raw page to file
        try:
            os.remove("Transcripts\\transcript2_"+str(i+1)+"_raw.txt")
        except:
            print("File "+str(i+1)+" raw didnt exist")
            
        with io.open("Transcripts\\transcript2_"+str(i+1)+"_raw.txt", "a", encoding="utf-8") as myfile:
            myfile.write(outputin)
        
        #Preprocess the output
        #Dark waters is incomplete... need different preprocessor
        if(names[i]== ' Dark Waters '):
            output = preprocess_wiki_UNOFF(outputin)
        else:
            output = preprocess_wiki(outputin)
        
        #write transcripts to file 
        try:
            os.remove("Transcripts\\transcript2_"+str(i+1)+".txt")
        except:
            print("File "+str(i+1)+" didnt exist")
            
        with io.open("Transcripts\\transcript2_"+str(i+1)+".txt", "a", encoding="utf-8") as myfile:
            myfile.write(output)
        with io.open("Transcripts\\transcript2_master.txt", "a", encoding="utf-8") as myfile:
            myfile.write(output)
            
        print(url)
        print(len(output))
        print(str(i+1)+" completed \n \n")
        if (len(output)<10):
            print(url)
            #print(len(outputin))
            #print(len(output))
            print("This one is empty: "+str(i+1)+"\n \n")
 
def preprocess_wiki(output):
    
    haspost = re.search('Post-Show\s+Edit', output)
    hasbreak = re.search('Break\s+Edit', output)
    hasstart = re.search('Part I\s+Edit', output)
    hasmid = re.search('Part II\s+Edit', output)
    if(hasstart == None):
        #and sometimes the transcript is different 
        hasstart = re.search('Part 1\s+Edit', output)
    if(hasstart == None):
        #or possibly this 
        hasstart =re.search('Part One\s+Edit', output)
        hasmid =re.search('Part Two\s+Edit', output)
        
    #haspost = output.count('Post-Show Edit')
    #hasbreak= output.count('Break Edit')
    #hasstart = output.count('Part I Edit')
    
    #print(hasstart)
    #print(hasmid)
    #print(hasbreak)
    #Split out the times when the show is actually going on: 
    last = output.find('NewPP')
    if(not haspost == None):
        last = haspost.start()
    
    if(not hasbreak == None):
        #given break, split on break
        if(not hasmid ==None):
            output = output[hasstart.start():hasbreak.start()]+output[hasmid.start():last]
        else:
            output = output[hasstart.start():hasbreak.start()]+output[hasstart.end():last]
    else:
        #given no break, split from start to end
        output = output[hasstart.start():last]
        
    #Remove headers
    re.sub('Pre-Show\s+Edit','', output)
    re.sub('Part II\s+Edit','', output)
    re.sub('Part I\s+Edit','', output)
    re.sub('Break\s+Edit','', output)
    output = output.replace(" NewPP ",'')
    
    output = tran_catch_name_mis(output)
    
    if (len(output)<10):
        print(hasstart)
        print(hasbreak)
        print(haspost)
    return output

def preprocess_wiki_UNOFF(output):
    
    last = output.find('NewPP')
    output = output[output.find("List of Transcripts"):last]
    output = output.replace(" NewPP ",'')
    output = output.replace("List of Transcripts",'')
    
    output = tran_catch_name_mis(output)
    return output

def tran_catch_name_mis(output):
    #Catch common name typos: 
    output = output.replace("MARISH ", "MARISHA")
    output = output.replace("BEAU", "MARISHA")
    output = output.replace("CALEB", "LIAM")
    output = output.replace("EVERYONE", "ALL")
    output = output.replace("CAST", "ALL")
    output = output.replace("MAT ", "MATT ")
    output = output.replace("MaTT", "MATT")
    output = output.replace(" ATT", "MATT")
    output = output.replace("MARIK", "MARK")
    output = output.replace("ASHLY", "ASHLEY")
    output = output.replace("ASHLYE", "ASHLEY")
    output = output.replace("SAN", "SAM")
    output = output.replace("NATT", "SAM")
    output = output.replace(" AURA", "LAURA")
    output = output.replace("NILA", "SUMALEE")
    output = output.replace("LTRAVIS", "TRAVIS")
    output = output.replace("AUDIENCE MEMBER", "AUDIENCE")
    output = output.replace("AND", "and")
    output = output.replace("&", "and")
    return output
    
main_page = get_page()
names = get_eps_names(main_page)
download_all(names)

