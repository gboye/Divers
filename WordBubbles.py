
# coding: utf-8

# In[3]:

#from unidecode import unidecode
import re
#import random as rd
import itertools as it


# In[4]:
bubbles=["emas","lttn","oeèyl","magte","csre"]
questions=[6,6,5,5]
solutions=["","",""]
reponses=[]
longReponses=[]
for q in questions:
    reponses.append(set())
    longReponses.append(0)

nomLexique="../../Copy/Python/phonemisation/bdlexique.txt"
fichierLexique=open(nomLexique)


# In[5]:

def sortLettres(mot):
    result=[]
#    stdMot=unidecode(mot)
    stdMot=mot
    for lettre in stdMot:
        result.append(lettre)
    result.sort()
    return "".join(result)


# In[6]:

def bonMot(mot):
    if re.search("[-']",mot):
         return False     
    else:
        return True


# In[7]:

mots={}
for element in fichierLexique:
    mot=element.split(";")[0]
    if bonMot(mot):
        longueurMot=len(mot)
        if not longueurMot in mots:
            mots[longueurMot]={}
        lettresMot=sortLettres(mot)
        if not lettresMot in mots[longueurMot]:
            mots[longueurMot][lettresMot]=set()
        mots[longueurMot][lettresMot].add(mot)


# In[8]:

def motsLettres(lettres,longueur):
    result=[]
    lettres=sortLettres(lettres)
    for retrait in range(longueur-1):
        l=longueur-retrait
        for comb in set(it.combinations(lettres,l)):
            cle="".join(comb)
            if cle in mots[l]:
                result.append(mots[l][cle])
    result.sort() 
    return result


# In[57]:

def Ngram(lot,n):
    result=[]
    if n<len(questions):
        longueur=questions[n]
        for ngram in set(it.combinations(lot,longueur)):
            mot=sortLettres("".join(ngram))
            if mot in mots[longueur]:
                reponses[n].add(str(mots[longueur][mot]))
#                print (n,mots[longueur][mot])
                reste=lot[:]
                for element in ngram:
                    reste.remove(element)
                suivant=Ngram(reste,n+1)
                if suivant:
                    result.append((mots[longueur][mot],suivant))
                else:
                    result.append(mots[longueur][mot])
    if result:
        if longReponses[n]<len(reponses[n]):
            print (n,reponses[n])
            longReponses[n]=len(reponses[n])
            print ("")
    return result


# In[1]:

lettres=""
for ligne in bubbles:
    lettres+=ligne
complet=[]
results=set()
for lettre in lettres:
    complet.append(lettre)
for num,solution in enumerate(solutions):
    if len(solution)>0:
        questions.remove(len(solution))
        reponses.pop(num)
    for lettre in solution:
        complet.remove(lettre)


# In[2]:

possibles=[]
Ngram(complet,0)


# In[ ]:




# In[ ]:



