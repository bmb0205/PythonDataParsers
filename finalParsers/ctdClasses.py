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

    def getInteractionActions(self):
        actionSet = set(self.columns[9].replace('^', '_').split('|'))
        return actionSet

    def getInteractionTypes(self):
        """ """
        typeSet = set()
        interactionTypeList = columns[9].split('|')
        for item in interactionTypeList:
            itemType = item.split('^')[0]
            typeSet.add(itemType)
        return typeSet




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
       
