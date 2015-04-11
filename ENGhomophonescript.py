#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import re
import sys
import codecs

f=codecs.open(sys.argv[1],"r", 'latin1')
#f=codecs.open("cmudict-0.7b","r", 'utf8')

vowels=["AA","AA0","AA1","AA2","AE","AE0","AE1",
"AE2","AH","AH0","AH1","AH2","AO","AO0","AO1","AO2",
"AW","AW0","AW1","AW2","AY","AY0","AY1","AY2","EH","EH0",
"EH1","EH2","ER","ER0","ER1","ER2","EY","EY0","EY1","EY2",
"IH","IH0","IH1","IH2","IY","IY0","IY1","IY2","OW","OW0",
"OW1","OW2","OY","OY0","OY1","OY2","UH","UH0","UH1",
"UH2","UW","UW0","UW1","UW2"]
#should i be creating a dico instead?
consonnes=["B","CH","D","DH","F","G","HH","JH","K","L",
"M","N","NG","P","R","S","SH","T","TH","V","W","Y","Z","ZH"]

dict={}
for line in f:
	#word=("{^.str$}  ")
	if ";;;" not in line: #delete header
		entry=line.split("  ")#every entry contains 2 spaces
		word=entry[0] #word is in first column
		syllabe=entry[1] #beginning of phonetic string in 2nd column
		if syllabe in dict:
			dict[syllabe].append(word)
		else:
			dict[syllabe]=[word]
	#phon=syllabe[" vowels "]

dict2={}

for el in dict:
	phons =el.split()
	if len(dict[el]) ==2 :
		for w in dict[el]:
			if len(w) ==len(phons):
				lilet = list(w)
				for i in range(0,len(w)):
					if phons[i] in dict2:
						dict2[phons[i]].append(lilet[i])
					else:
						dict2[phons[i]]=[lilet[i]]
#to end this part, create a new loop and print results
for t in dict2:
	print(t,set(dict2[t]))
#Currently script creates a list of orthographic possibilities
#for each phoneme with mistakes galore!
#Next: Need to divide into stacks:
# Transcription with multiple spellings:
#a.) Letters that have the same phonetic transcriptions (mostly vowels) 
#b.)Letters that have different phonetic transciptions (consonnes)
#example="ababa"
#diffspelling=[]
#for vowel in example:
	#if vowel not in word:
	#diffspelling.append(word)
	#diffspelling.sort()
#choix=[]²
#print choix

