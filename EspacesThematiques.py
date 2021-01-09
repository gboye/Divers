#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Codage IPA

cSAMPA=u"SZNJêôârEHO692"
cIPA=[u"ʃ",u"ʒ",u"ŋ",u"ɲ",u"ɛ̃",u"ɔ̃",u"ɑ̃",u"ʁ",u"ɛ",u"ɥ",u"ɔ",u"ə",u"œ",u"ø"]

import unicodedata
def listerUnicode(chaine):
    result=[]
    comb=False
    prec=u""
    for char in chaine:
        print char,
        if unicodedata.combining(char):
            result.append(prec+char)
            prec=""
        else:
            result.append(prec)
            prec=char
    result.append(prec)
    return [r for r in result if r!=""]

ipaIn = listerUnicode(cSAMPA)
ipaOut= cIPA
toipa = dict(zip(ipaIn, ipaOut))

def coderIPA(chaine,table=toipa):
    result=chaine
    for k in table:
        result=result.replace(k,table[k])
    return result


# Tabular de conjugaison

etColours=["orange",
           "brown!50",
           "brown",
           "blue!10",
           "yellow!50",
           "blue!25",
           "teal!50",
           "blue!50",
           "cyan!50",
           "lime",
           "pink",
           "magenta!50",
          ]
'''
Correspondances entre les couleurs de LaTeX et les couleurs HTML
'''
etColoursHTML={
                "orange":0xFF8000,
                "brown!50":0xdfbf9f,
                "brown":0xbf8040,
                "blue!10":0xe5e5ff,
                "yellow!50":0xffff80,
                "blue!25":0xbfbfff,
                "teal!50":0x80bfbf,
                "blue!50":0x8080ff,
                "cyan!50":0x80ffff,
                "lime":0xbfff00,
                "pink":0xffbfbf,
                "magenta!50":0xff80ff,
}

etCells=[
    ["ii"+p+n for n in "SP" for p in "123"]+["pi1P","pi2P"],
    ["pi3P"],
    ["pi"+p+"S" for p in "123"],
    ["pP"],
    ["pI2S"],
    ["pI1P","pI2P"],
    ["ps"+p+"S" for p in "123"]+["ps3P"],
    ["ps1P","ps2P"],
    ["inf"],
    ["fi"+p+n for n in "SP" for p in "123"]+["pc"+p+n for n in "SP" for p in "123"],
    ["ai"+p+n for n in "SP" for p in "123"]+["is"+p+n for n in "SP" for p in "123"],
    ["pp"+g+n for g in "MF" for n in "SP"],
        ]

etCols=[c for et in etCells for c in et]

#=======================================================================
# modifié le 25/08/20 pour changer l'ordre des colonnes
#
persons=[p+n for n in "SP" for p in "123" ]
etCols=[t+p for t in "pi ii fi pc ps ai is".split(" ") for p in persons]
etCols+="pI2S pI1P pI2P inf pP".split(" ")
etCols+=["pp"+g+n for g in "MF" for n in "SP"]
#=======================================================================
tabTemps={
    "pi":u"ind. prs",
    "ii":u"ind. ipf",
    "ai":u"ind. ps",
    "fi":u"ind. fut",
    "ps":u"subj. prs",
    "is":u"subj. ipf",
    "pc":u"cond. prs",
    "pI":u"imper. prs",
    "inf":u"non-fini"
    }
dictEtColours={}
for nET,ET in enumerate(etCells):
    for c in ET:
        dictEtColours[c]=etColours[nET]
#dictEtColours

latex2RGB={"orange":(240,134,51),
           "brown!50":(218,192,163),
           "brown":(182,130,75),
           "blue!10":(230,230,253),
           "yellow!50":(255,246,164),
           "blue!25":(191,192,250),
           "teal!50":(141,190,190),
           "blue!50":(128,129,247),
           "cyan!50":(133,198,227),
           "lime":(204,252,81),
           "pink":(246,194,193),
           "magenta!50":(221,151,180),
          }
etRGB=[
        (240,134,51),
        (218,192,163),
        (182,130,75),
        (230,230,253),
        (255,246,164),
        (191,192,250),
        (141,190,190),
        (128,129,247),
        (133,198,227),
        (204,252,81),
        (246,194,193),
        (221,151,180),
       ]
etRGBx=[(r/255.,g/255.,b/255.) for r,g,b in etRGB]

cellColors={}
for nEt,et in enumerate(etCells):
    for c in et:
        cellColors[c]=etRGBx[nEt]



def makeTabularParadigmeDF(lexeme,lDF,dictColours,title="",coulLim=False, cat="V",dictMorphomes={},ipa=True):
    row=lDF[lDF["lexeme"]==lexeme.encode("utf8")]
    return makeTabularParadigme(row,dictColours,title="",coulLim=False, cat="V",dictMorphomes={},lexeme=lexeme,ipa=ipa)

def makeTabularParadigme(row,dictColours,title="",coulLim=False, cat="V",dictMorphomes={},lexeme="",ipa=True):
    tabular=[]
    def makeValue(case):
#        if len(row[case])>0 and len(row[case].values[0])>0:
        if case in row and all(row[case].notnull()):
            if ipa:
                result=coderIPA(row[case].values[0])
            else:
                result=int(row[case].values[0])
        elif dictMorphomes!={} and case in dictMorphomes:
            altCase=dictMorphomes[case][0]
            if len(row[altCase])>0 and len(row[altCase].values[0])>0:
                if ipa:
                    result=coderIPA(row[altCase].values[0])
                else:
                    result=int(row[case].values[0])
            else:
                result="?"
        else:
            result="?"
        return result

    def makeLine6(tenseCode):
        line=[tabTemps[tenseCode]]
        for person in [per+nb for nb in ["S","P"] for per in ["1","2","3"]]:
            case=tenseCode+person
            if case in dictColours:
                line.append(r"\cellcolor{%s}%s"%(dictColours[case],makeValue(case)))
            else:
                line.append(r"\cellcolor{%s}%s"%("black",makeValue(case)))
        return r" & ".join(line)+r"\\"

    def makeLine3(tenseCode):
        line=[tabTemps[tenseCode]]
        for person in [per+nb for nb in ["S","P"] for per in ["1","2","3"]]:
            if person in ["2S","1P","2P"]:
                case=tenseCode+person
                if case in dictColours:
                    line.append(r"\cellcolor{%s}%s"%(dictColours[case],makeValue(case)))
                else:
                    line.append(r"\cellcolor{%s}%s"%("black",makeValue(case)))
#                line.append(r"\cellcolor{%s}%s"%(dictColours[case],case))
            else:
                line.append(r"---")
        return r" & ".join(line)+r"\\"

    def makeLineNF():
        line=["non-fini"]
        for case in ["inf","pP","ppMS","ppMP","ppFS","ppFP"]:
            if case in dictColours:
                line.append(r"\cellcolor{%s}%s"%(dictColours[case],makeValue(case)))
            else:
                line.append(r"\cellcolor{%s}%s"%("black",makeValue(case)))
#            line.append(r"\cellcolor{%s}%s"%(dictColours[case],case))
        return r" & ".join(line)+r"\\"

    def makeLineMF(nombre):
        line=[]
        for genre in "mf":
            case=genre+nombre
            if case in dictColours:
                line.append(r"\cellcolor{%s}%s"%(dictColours[case],makeValue(case)))
            else:
                line.append(r"\cellcolor{%s}%s"%("black",makeValue(case)))
        return r" & ".join(line)+r"\\"

    def makeLineCoulLim():
        line=[]
        for numLimite,limite in enumerate(listLimites):
            line.append(r"\cellcolor{%s}%s"%(listLimCoul[numLimite],"$<$"+str(limite)))
        return r"\hline\hline "+r" & ".join(line)+r"\\"

    if cat=="V":
        top=[
            r"\begin{center}",
            r"\begin{tabular}{ccccccc}",
            r"\toprule",
            " & ".join([ur"\textsc{%s}"%lexeme]+[p+n for n in ["sg","pl"] for p in "123" ])+r"\\",
            r"\midrule"
            ]
        bottom=[
            r"\bottomrule",
            r"\end{tabular}\\",
            title,
            r"\end{center}",
            r"\bigskip",
            r""
            ]
        tabular.append("\n".join(top))
        for tenseCode in ["pi","ii","fi","pc", "ps","ai", "is"]:
            tabular.append(makeLine6(tenseCode))
        tabular.append(makeLine3("pI"))
        tabular.append(u"\midrule\n")
        tabular.append(ur"& inf. & part. prés. & \multicolumn{4}{c}{part. passé}\\")
        tabular.append(makeLineNF())
    elif cat=="A":
        top=[
            r"\begin{center}",
            r"\begin{tabular}{cc}",
            r"\toprule"
            ]
        bottom=[
            r"\bottomrule",
            r"\end{tabular}\\",
            title,
            r"\end{center}",
#            r"\bigskip",
            r""
            ]
        tabular.append("\n".join(top))
        for number in "sp":
            tabular.append(makeLineMF(number))
    if coulLim:
        tabular.append(makeLineCoulLim())
    tabular.append("\n".join(bottom))
    return "\n".join(tabular)

def colorerXTicks(gAX,fSize=12):
    xlabels=gAX.get_xticklabels()
    for xlabel in xlabels:
        xtext=xlabel.get_text()
        xlabel.set_backgroundcolor(cellColors[xtext])
        xlabel.set_family("monospace")

def sortCells(cells):
    return sorted(cells,key=lambda x: etCols.index(x))
