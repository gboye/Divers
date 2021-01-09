# -*- coding: utf-8 -*-

#
# Déclarations incluses
#
import re
import pandas as pd
import itertools as it
from ipywidgets import FloatProgress


swimColorsHTML={
                "data":0x80ffff,
                "data2":0xbfbfff,
                "TP":0xbfff00,
                "TP2":0xdfff80,
                "FP":0xff6666,
                "FP2":0xff9999,
                "UG":0xffff80,
                "UG2":0xff8000,
                "OG":0xff80ff,
                "OG2":0xffbfbf,
                "none":0xffffff,
                "nocell":0xbfbfbf
}

# Préparation du calcul des analogies
### Calcul de la différence entre deux formes

def diff(mot1,mot2):
    result=[]
    diff1=""
    diff2=""
    same=""
    vide="."
    lmax=max(len(mot1),len(mot2))
    lmin=min(len(mot1),len(mot2))
    for index in range(lmax):
        if index < lmin:
            if mot1[index]!=mot2[index]:
                diff1+=mot1[index]
                diff2+=mot2[index]
                same+=vide
            else:
                same+=mot1[index]
                diff1+=vide
                diff2+=vide
        elif index < len(mot1):
            diff1+=mot1[index]
        elif index < len(mot2):
            diff2+=mot2[index]
    diff1=diff1.lstrip(".")
    diff2=diff2.lstrip(".")
#    return (same,diff1,diff2,diff1+"_"+diff2)
    return (diff1+"-"+diff2)

### Accumulation des paires appartenant à un patron

def rowDiff(row, patrons):
    result=diff(row[0],row[1])
    if not result in patrons:
        patrons[result]=(formesPatron(),formesPatron())
    patrons[result][0].ajouterFormes(row[0])
    patrons[result][1].ajouterFormes(row[1])
    return (result[0],result[1])

### Transformation d'un patron en RegExp

def patron2regexp(morceaux):
    result="^"
    for morceau in morceaux:
        if morceau=="*":
            result+="(.*)"
        elif len(morceau)>1:
            result+="(["+morceau+"])"
        else:
            result+=morceau
    result+="$"
    result=result.replace(")(","")
    return result

### Substitution de sortie

def remplacementSortie(sortie):
    n=1
    nsortie=""
    for lettre in sortie:
        if lettre==".":
            nsortie+="\g<%d>"%n
            n+=1
        else:
            nsortie+=lettre
    return nsortie


class formesPatron:
    '''
    Accumulateur de formes correspondant à un patron pour calcul de la Généralisation Minimale (cf. MGL)
    '''
    def __init__(self):
        self.formes=[]

#    def __repr__(self):
#        return ','.join(self.calculerGM())

    def ajouterForme(self,forme):
        self.formes.append(forme)

    def calculerGM(self):
        minLongueur=len(min(self.formes, key=len))
        maxLongueur=len(max(self.formes, key=len))
        # if debug: print (minLongueur, maxLongueur, file=logfile)
        positions=[]
        if maxLongueur>minLongueur:
            positions.append("*")
        for i in xrange(minLongueur, 0, -1):
            phonemes=set([x[-i] for x in self.formes])
            # if debug: print (phonemes, file=logfile)
            if "." in phonemes:
                positions.append(".")
            else:
                positions.append("".join(fs.lattice[phonemes].extent))
        return patron2regexp(positions)

class pairePatrons:
    '''
    Accumulateur de triplets (f1,f2,patron) correspondant à une paire pour calcul des Généralisations Minimales (cf. MGL)
    '''
    def __init__(self,case1,case2):
        self.patrons1={}
        self.patrons2={}
        self.case1=case1
        self.case2=case2

#    def __repr__(self):
#        return ','.join(self.calculerGM())

    def ajouterFormes(self,forme1,forme2,patron):
#        print (forme1,forme2,patron, file=logfile)
        patron12=patron
        (pat1,pat2)=patron.split("-")
        patron21=pat2+"-"+pat1
#        print (patron12,patron21, file=logfile)
        if not patron12 in self.patrons1:
            self.patrons1[patron12]=formesPatron()
        self.patrons1[patron12].ajouterForme(forme1)
        if not patron21 in self.patrons2:
            self.patrons2[patron21]=formesPatron()
        self.patrons2[patron21].ajouterForme(forme2)


    def calculerGM(self):
        resultat1={}
        for patron in self.patrons1:
            # if debug: print ("patron1", patron, file=logfile)
            resultat1[patron]=self.patrons1[patron].calculerGM()
        resultat2={}
        for patron in self.patrons2:
            # if debug: print ("patron2", patron, file=logfile)
            resultat2[patron]=self.patrons2[patron].calculerGM()
        return (resultat1,resultat2)

# Classe pour la gestion des patrons, des classes et des transformations

class paireClasses:
    def __init__(self,case1,case2):
        self.case1=case1
        self.case2=case2
        self.nom=case1+"-"+case2
        self.classes1=classesPaire(case1,case2)
        self.classes2=classesPaire(case2,case1)

    def ajouterPatron(self,n,patron,motif):
        if n==1:
            self.classes1.ajouterPatron(patron,motif)
        elif n==2:
            self.classes2.ajouterPatron(patron,motif)
        # else:
        #     if debug: print ("le numéro de forme n'est pas dans [1,2]",n, file=logfile)

    def ajouterPaire(self,forme1,forme2):
        self.classes1.ajouterPaire(forme1,forme2)
        self.classes2.ajouterPaire(forme2,forme1)

    def calculerClasses(self):
        return(self.classes1,self.classes2)


class classesPaire:
    '''
    Gestion des patrons, des classes et des transformations

    ajouterPatron : ajoute un patron et son motif associé (MGL)
    ajouterPaire : ajoute une paire de formes, calcule la classe de la forme1 et la règle sélectionnée
    sortirForme : cacule les formes de sortie correspondant à la forme1 avec leurs coefficients respectifs
    '''
    def __init__(self,case1,case2):
        self.case1=case1
        self.case2=case2
        self.nom=case1+"-"+case2
        self.classe={}
        self.nbClasse={}
        self.patrons={}
        self.entree={}
        self.sortie={}
        self.classeCF={}
        self.nbClasseCF={}

    def ajouterPatron(self,patron,motif):
        self.patrons[patron]=motif
        (entree,sortie)=patron.split("-")
        self.entree[patron]=entree.replace(u".",u"(.)")
        self.sortie[patron]=remplacementSortie(sortie)

    def ajouterPaire(self,forme1,forme2):
        '''
        on calcule la classe de la paire idClasseForme et la règle sélectionnée
        on incrémente le compteur de la classe et celui de la règle sélectionnée à l'intérieur de la classe
        '''
        classeFormeCF=[]
        regleFormeCF=""
        classeForme=[]
        regleForme=""
        for patron in self.patrons:
            filterF1=".*"+patron.split("-")[0]+"$"
            if re.match(filterF1,forme1):
                classeFormeCF.append(patron)
                if forme2==re.sub(self.entree[patron]+"$",self.sortie[patron],forme1):
                    regleFormeCF=patron
            filterF1=self.patrons[patron]
            if re.match(filterF1,forme1):
                classeForme.append(patron)
                '''
                le +"$" permet de forcer l'alignement à droite pour les transformations suffixales
                '''
                if forme2==re.sub(self.entree[patron]+"$",self.sortie[patron],forme1):
                    regleForme=patron
        idClasseFormeCF=", ".join(classeFormeCF)
        if not idClasseFormeCF in self.classeCF:
            self.classeCF[idClasseFormeCF]={}
            self.nbClasseCF[idClasseFormeCF]=0
        if not regleFormeCF in self.classeCF[idClasseFormeCF]:
            self.classeCF[idClasseFormeCF][regleFormeCF]=0
        self.nbClasseCF[idClasseFormeCF]+=1
        self.classeCF[idClasseFormeCF][regleFormeCF]+=1

        idClasseForme=", ".join(classeForme)
        if not idClasseForme in self.classe:
            self.classe[idClasseForme]={}
            self.nbClasse[idClasseForme]=0
        if not regleForme in self.classe[idClasseForme]:
            self.classe[idClasseForme][regleForme]=0
        self.nbClasse[idClasseForme]+=1
        self.classe[idClasseForme][regleForme]+=1

    def sortirForme(self,forme,contextFree=True):
        classeForme=[]
        sortieForme={}
        for patron in self.patrons:
            if contextFree:
                # m=re.match(ur"^[^.*\[\]()]*$",self.patrons[patron]) # désactivation des règles à scope=1
                # if m:
                #     break
                filterF1=".*"+patron.split("-")[0]+"$"
            else:
                filterF1=self.patrons[patron]
            # print ("filtre",filterF1)
            if re.match(filterF1,forme):
                classeForme.append(patron)
        # print ("classeForme",classeForme)
        if classeForme:
            idClasseForme=", ".join(classeForme)
            if not contextFree:
                nbClasse=self.nbClasse
                classe=self.classe
            if not contextFree and idClasseForme in nbClasse :   # modifié le 4/9/2020 pour permettre les modifications contextFree sans préjudice de classe
                nTotal=nbClasse[idClasseForme]
                for patron in classe[idClasseForme]:
                    sortie=re.sub(self.entree[patron]+"$",self.sortie[patron],forme)
                    sortieForme[sortie]=float(classe[idClasseForme][patron])/nTotal
            else:
                # if debug:
                    # print (forme, file=logfile)
                    # print ("pas de classe",idClasseForme, file=logfile)
                    # print ("%.2f par forme de sortie" % (float(1)/len(classeForme)), file=logfile)
                nTotal=len(classeForme)
                for patron in classeForme:
                    sortie=re.sub(self.entree[patron]+"$",self.sortie[patron],forme)
                    sortieForme[sortie]=float(1)/nTotal
        # else:
            # if debug:
            #     print (forme, file=logfile)
            #     print ("pas de patron", file=logfile)
        return sortieForme


def splitCellMates(df,colonne):
    '''
    Calcul d'une dataframe sans surabondance par dédoublement des valeurs
    '''
    test=df.reset_index()
    del test["index"]
    splitIndexes=[]
    for index,ligne in test.iterrows():
        if "," in ligne[colonne]:
            valeurs=set(ligne[colonne].split(","))
            nouvelleLigne=ligne
            for valeur in valeurs:
                nouvelleLigne[colonne]=valeur
                test=test.append(nouvelleLigne,ignore_index=True)
            splitIndexes.append(index)
    if splitIndexes:
        test=test.drop(test.index[splitIndexes])
    return test

def rapports(paradigme):
    if len(paradigme.columns.values.tolist())==2:
        (case1,lexeme)= paradigme.columns.values.tolist()
        case2=case1
    else:
        (case1,case2,lexeme)= paradigme.columns.values.tolist()
    patrons=pairePatrons(case1,case2)
    classes=paireClasses(case1,case2)
    if len(paradigme)>0:
        paradigme.apply(lambda x: patrons.ajouterFormes(x[case1],x[case2],diff(x[case1],x[case2])), axis=1)
        (regles1,regles2)=patrons.calculerGM()
        for regle in regles1:
            classes.ajouterPatron(1,regle,regles1[regle])
        for regle in regles2:
            classes.ajouterPatron(2,regle,regles2[regle])
        paradigme.apply(lambda x: classes.ajouterPaire(x[case1],x[case2]), axis=1)
    (classes1,classes2)=classes.calculerClasses()
    return (classes1,classes2)

def evaluerEchantillon(paradigmes):
    result={}
    colonnes=paradigmes.columns.values.tolist()
    for n,paire in enumerate(it.combinations_with_replacement(sampleCases,2)):
        progressBar.value=n
        # if debug: print (paire, file=logfile)
        # if debug: print ("-".join(paire),end=", ")
        paireListe=list(paire)
        paireListe.append("lexeme")
        if paire[0] in colonnes and paire[1] in colonnes:
            paradigmePaire=paradigmes[paireListe].dropna(thresh=3, axis=0).reindex()
            if paire[0]==paire[1]:
                paireListe[1]="TEMP"
                paradigmePaire.columns=paireListe
            paradigmePaire=splitCellMates(splitCellMates(paradigmePaire,paireListe[0]),paireListe[1])
            result[paire]=rapports(paradigmePaire)
        else:
            result[paire]=("missing pair", paire)
    return result
