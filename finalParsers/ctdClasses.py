#!/usr/bin/python

"""
##################################################################################################################
##########################################   CTD Parser Classes   #########################################################
##################################################################################################################

Written by: Brandon Burciaga

* Module imported by taxonomyParser.py for NCBI Taxnomy node and relationship creation.
* Holds classes TaxNamesParser, TaxNodesParser, TaxCitationsParser

"""


class ChemGeneIXNS(object):
    """ creates object for names.dmp """
    def __init__(self, columns):
        self.columns = columns
        self.meshID = columns[1]
        self.entrezGeneID = columns[4]
        self.interaction = columns[8]
        self.pubmedID = columns[10].replace('|', ';')

    def getInteractionActions(self):
        actionSet = set(self.columns[9].replace('^', '_').split('|'))
        return actionSet

    def getInteractionTypes(self):
        """ """
        typeSet = set()
        interactionTypeList = self.columns[9].split('|')
        for item in interactionTypeList:
            itemType = item.split('^')[0]
            typeSet.add(itemType)
        return typeSet

    def getOrganism(self):
        if self.columns[6] is not None:
            return self.columns[6]
        else:
            return ''

    def getOrganismID(self):
        if self.columns[7] is not None:
            return self.columns[7]
        else:
            return ''


class ChemDisease(object):
    """ """
    def __init__(self, columns):
        self.columns = columns
        self.meshID = columns[1]
        self.endID = columns[4]
        self.evidence = columns[5]
        self.inferenceGeneSymbol = columns[6]
        self.inferenceScore = columns[7]

    def getEndID(self):
        if self.endID.startswith('MESH'):
            return self.endID[5:]
        elif self.endID.startswith('OMIM'):
            return self.endID




# class ChemGeneIXNS(object):
#     """ creates object for names.dmp """
#     def __init__(self, columns):
       
# class ChemGeneIXNS(object):
#     """ creates object for names.dmp """
#     def __init__(self, columns):
       
# class ChemGeneIXNS(object):
#     """ creates object for names.dmp """
#     def __init__(self, columns):
       
# class ChemGeneIXNS(object):
#     """ creates object for names.dmp """
#     def __init__(self, columns):
       
