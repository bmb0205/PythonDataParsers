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
        self.meshID = self.columns[1].strip()
        self.entrezGeneID = self.columns[4].strip()
        self.interaction = self.columns[8].strip()

    def getInteractionActions(self):
        actions = set(self.columns[9].replace('^', '_').split('|'))
        return actions

    def getInteractionTypes(self):
        """ """
        typeSet = set()
        interactionTypeList = self.columns[9].split('|')
        for item in interactionTypeList:
            itemType = item.split('^')[0]
            typeSet.add(itemType)
        return typeSet

class IxnType(object):
    def __init__(self, columns):
        self.columns = columns
        self.typeName = columns[0]
        self.code = columns[1]
        self.description = columns[2]

    def getParentCode(self):
        if len(self.columns) == 3:
            return ''
        return self.columns[3]



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
       
