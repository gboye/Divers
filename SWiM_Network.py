# -*- coding: utf-8 -*-
import re
import networkx as nx
import itertools as it
import pandas as pd

class paradigmeDistribution():
    '''
    Gestion des distributions dans les cases du paradigme
    '''

    def __init__(self,lexeme,analyseCases):
        self.lexeme=lexeme
        self.formes={i:{} for i in analyseCases}

    def ajouterFormes(self,case,formes,coef=1.0):
        for forme in formes:
            if not forme in self.formes[case]:
                self.formes[case][forme]=0
            self.formes[case][forme]+=formes[forme]*coef

    def normaliserDistributions(self,caseListe):
        normalesDistributions={i:{} for i in caseListe}
        for case in caseListe:
            total=0
            for element in self.formes[case]:
                total+=self.formes[case][element]
            for element in self.formes[case]:
                normalesDistributions[case][element]=float(self.formes[case][element])/total
        return normalesDistributions


def ajouterPoint(lexeme,forme,case,digraphe,graphe):
    pointName="%s-%s-%s"%(lexeme,forme,case)
#    if not pointName in digraphe.nodes():
    tam=case[:2]
    if tam=="in": tam="inf"
    digraphe.add_node(pointName, tam='"%s"'%tam)
    graphe.add_node(pointName, tam='"%s"'%tam)
    return pointName

def ajouterFleche(pointDepart,pointSortie,coef,digraphe,graphe):
    digraphe.add_edge(pointDepart,pointSortie,weight=float(coef))
    if digraphe.has_edge(pointSortie,pointDepart):
        # coefGraphe=float(digraphe.edge[pointSortie][pointDepart]["weight"]+coef)/2
        coefGraphe=float(digraphe[pointSortie][pointDepart]["weight"]+coef)/2
        graphe.add_edge(pointDepart,pointSortie,weight=coefGraphe)


def generateRowForms(row,contextFree):
    candidateForms=paradigmeDistribution(row["lexeme"],analyseCases)
    for caseDepart,formeDepart in row.dropna().iteritems():
        if caseDepart!="lexeme":
            for case in analyseCases:
                if "," in formeDepart:                  # Gérer les cas de surabondance
                    surFormes=formeDepart.split(",")
                    for surForme in surFormes:
                        candidateForms.ajouterFormes(case,analyseRules[(caseDepart, case)].sortirForme(surForme,contextFree))
                else:
                    candidateForms.ajouterFormes(case,analyseRules[(caseDepart, case)].sortirForme(formeDepart,contextFree))
    rowForms=candidateForms.normaliserDistributions(analyseCases)
    return rowForms


def generateRowParadigm(row,rowForms,contextFree):
    lexeme=row["lexeme"]
#     distributionInitiale=rowForms
    candidats=paradigmeDistribution(lexeme,analyseCases)
    digraphe=nx.DiGraph()
    graphe=nx.Graph()
    for caseDepart in analyseCases:
        for formeDepart in rowForms[caseDepart]:
            if formeDepart:
                pointDepart=ajouterPoint(lexeme,formeDepart,caseDepart,digraphe,graphe)
                coefDepart=rowForms[caseDepart][formeDepart]
                # if debug: print (caseDepart,formeDepart, file=logfile)
                for caseSortie in analyseCases:
                    distributionSortieBrute=analyseRules[(caseDepart, caseSortie)].sortirForme(formeDepart,contextFree)
                    if distributionSortieBrute:
#                         if not genDigraphe:
# #                            print ("brute",distributionSortieBrute)
#                             distributionSortie={f:distributionSortieBrute[f] for f in distributionSortieBrute if f in distributionInitiale[caseSortie]}
#                         else:
                        distributionSortie=distributionSortieBrute
#                        print ("filtre",distributionSortie)
#                        print (distributionInitiale[caseSortie])
                        # if debug: print (caseSortie,distributionSortie,distributionInitiale[caseDepart], file=logfile)
                        candidats.ajouterFormes(caseSortie,distributionSortie,rowForms[caseDepart][formeDepart])
                        for formeSortie in distributionSortie:
                            pointSortie=ajouterPoint(lexeme,formeSortie,caseSortie,digraphe,graphe)
                            coefSortie=distributionSortie[formeSortie]
                            ajouterFleche(pointDepart,pointSortie,float(coefDepart*coefSortie),digraphe,graphe)
    return (candidats,digraphe,graphe)


def bruteCliques(cliques,maxCliqueSize=51):
    cliquesBrutes={n+1:0 for n in range(maxCliqueSize)}
    for l in lexCliques:
        longueur=len(l)
        if longueur>1:
            if not longueur in cliquesBrutes:
                cliquesBrutes[longueur]=0
            cliquesBrutes[longueur]+=1
    return cliquesBrutes

def getFaithfulCliques(row,cliques):
    result=[]
    lexeme=row["lexeme"]
    originalForms=[]
    for k,v in row.dropna().iteritems():
        if k!="lexeme":
            if "," not in v:
                originalForms.append(u"%s-%s-%s"%(lexeme,v,k))
            else:
                surVs=v.split(",")
                for surV in surVs:
                    originalForms.append(u"%s-%s-%s"%(lexeme,surV,k))
    # print ("originalForms",originalForms)
    for clique in cliques:
        faithful=True
        for originalForm in originalForms:
            # if "," in originalForm:
            #     print (originalForm,clique)
            if originalForm not in clique:
                faithful=False
                break
        if faithful:
            result.append(clique)
    return result

def sortCliques(cliques):
    result={}
    for clique in cliques:
        lClique=len(set([c.rsplit("-",1)[1] for c in clique]))
        if lClique not in result:
            result[lClique]=[]
        result[lClique].append(clique)
    return result

def cliqueScore(clique,graphe):
    score=0
    if len(clique)>1:
        for (depart,arrivee) in it.combinations_with_replacement(clique,2):
            score+=graphe[depart][arrivee]["weight"]
    return score

def getMaxScoreClique(cliques,graphe):
    maxScore=0
    result=[]
    for clique in cliques:
        scoreClique=cliqueScore(clique,graphe)
        if scoreClique>maxScore:
            result=[clique]
        elif scoreClique==maxScore:
            result.append(clique)
    return result

def completeMaxClique(dCliques,cliquesMax,seuilClique=1):
    return cliquesMax[0]
#     result=[]
#     maxLen=len(clique)
#     for l in range(seuilClique):
#         i=maxLen-l-1
#         if i in dCliques:
#             result.extend(dCliques[i])
#     return result

def splitCliqueNode(cliqueNode):
    nodeChunks=cliqueNode.split("-")
    if len(nodeChunks)<3:
        print (cliqueNode,nodeChunks)
    lexeme="-".join(nodeChunks[:-2])
    forme=nodeChunks[-2]
    case=nodeChunks[-1]
    return (lexeme,forme,case)

def dictCliqueForms(clique):
    result={}
    for element in clique:
        lexeme,forme,case=splitCliqueNode(element)
        if "lexeme" not in result:
            result["lexeme"]=[lexeme]
        for c in omp2msp[case]:
            if c in result:
                result[c].append(forme)
            else:
                result[c]=[forme]
    result={k:",".join(sorted(v)) for k,v in result.iteritems()}
    return result



def generateFromTrial(trialFormes,contextFree):
    newRows=[]
    for iRow,row in trialFormes.iterrows():
        lexeme=row["lexeme"]
        # print (iRow,lexeme)
        # générer les formes à partir des connaissances
        rowForms1=generateRowForms(row,contextFree)

        # construire le graphe pondéré de la génération des formes entre elles
        rowForms2,digraphe,graphe=generateRowParadigm(row,rowForms1,contextFree)

        # extraire les cliques maximales
        lexCliques=list(nx.algorithms.clique.find_cliques(graphe))

        # sélectionner les cliques fidèles
        faithfulCliques=getFaithfulCliques(row,lexCliques)

        if faithfulCliques:
            # trier les cliques par tailles
            sortedCliques=sortCliques(faithfulCliques)
            maxLen=max(sortedCliques)
            maxCliques=sortedCliques[maxLen]

            # sélectionner les cliques avec le meilleur score
            maxClique=getMaxScoreClique(maxCliques,graphe)

            # finaliser une clique avec les cliques max et les complémentaires
            finalClique=completeMaxClique(sortedCliques,maxClique)

            # transformer la clique en dictRow
            dictRow=dictCliqueForms(finalClique)
            newRows.append(dictRow)
        else:
            newRows.append(row.to_dict())
    # display(newRows)
    trialGen=pd.DataFrame(newRows)
    inCases=trialGen.columns
    outCases=list(set(analyseCases)-set(inCases))
    trialGen=pd.concat([trialGen,pd.DataFrame(columns=outCases)],sort=False)
    trialGen=trialGen[["lexeme"]+analyseCases]
    #
    # Attention, la normalisation interagit avec les règles
    # il faut conserver le même codage qui celui utilisé pour la
    # génération des règles...
    #
#     trialGen=normalizePhono(trialGen,tableNeutralise)
    return trialGen
