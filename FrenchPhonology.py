# -*- coding: utf-8 -*-

import re


def setNeutralisation(phonologicalMap):
    neutralisationsNORD=(u"6û",u"9ê")
    neutralisationsSUD=(u"e2o",u"E9O")
    if phonologicalMap==u"N":
        neutralisations=neutralisationsNORD
    elif phonologicalMap==u"S":
        neutralisations=neutralisationsSUD
    elif phonologicalMap==u"NS":
        neutralisations=(neutralisationsNORD[0]+neutralisationsSUD[0],neutralisationsNORD[1]+neutralisationsSUD[1])
    else:
        neutralisations=(u"",u"")
        phonologicalMap=("X")
    bdlexiqueIn = unicode(u"èò"+neutralisations[0])
    bdlexiqueNum = [ord(char) for char in bdlexiqueIn]
    neutreOut = unicode(u"EO"+neutralisations[1])
    neutralise = dict(zip(bdlexiqueNum, neutreOut))
    return neutralise

def recoder(chaine,table):
    if type(chaine)==str:
        temp=unicode(chaine.decode('utf8')).translate(table)
        result=temp.encode('utf8')
    elif type(chaine)==unicode:
        result=chaine.translate(table)
    else:
        result=chaine
    return result

dierese={"j":"ij", "w":"uw","H":"yH","i":"ij","u":"uw","y":"yH"}
glideSchwa={"j6":"i", "w6":"u","H6":"y"}

sampaIn = u"629EOêâôûSZJrH"
oSampaIn = [ord(char) for char in sampaIn]
ipaOut = u"ə ø œ ɛ ɔ ɛ̃ ɑ̃ ɔ̃ œ̃ ʃ ʒ ɲ ʁ ɥ".split(" ")
toipa = dict(zip(oSampaIn, ipaOut))

def makeFrench(prononciation,table):
    glide2voyelle={"j":"i","w":"u","H":"y"}
    if prononciation==prononciation and prononciation:
        if "," in prononciation:
            prononciations=prononciation.split(",")
            setPrononciations=set()
            for element in prononciations:
                setPrononciations.add(makeFrench(element,table))
            result=",".join(list(setPrononciations))
        else:
            result=prononciation
            m=re.match(ur"(.*[ptkbdgfsSvzZrl])([jwH]6)(.*)",result)
            if m:
                result=m.group(1)+glideSchwa[m.group(2)]+m.group(3)
            result=recoder(result,table)
            result=result.replace("jj","j")
            m=re.match(ur"^(.*[^ieèEaOouy926êôâ])([jwH])$",result)
            if m:
                # print ("pb avec un glide final après consonne", prononciation)
                voyelle=glide2voyelle[m.group(2)]
                result=m.group(1)+voyelle
            m=re.match(ur"(.*[ptkbdgfsSvzZ][rl])([jwH])(.*)",result)
            if m:
                n=re.search(ur"[ptkbdgfsSvzZ][rl](wa|Hi|wê)",result)
                if not n:
                    glide=m.group(2)
                    result=m.group(1)+dierese[glide]+m.group(3)
            m=re.match(ur"(.*)([iuy])([ieEaOouy].*)",result)
            if m:
                glide=m.group(2)
                result=m.group(1)+dierese[glide]+m.group(3)
            result=result.replace("Jj","J")
    else:
        result=prononciation
    return result

def normalizePhono(lDF,table):
    dfResult=lDF.copy()
    lCases=lDF.columns.tolist()
    if "lexeme" in lCases:
        lCases.remove("lexeme")
    for case in lCases:
        dfResult[case]=dfResult[case].apply(lambda x: makeFrench(x,table))
    return dfResult
