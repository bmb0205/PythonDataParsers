#!/usr/bin/python

"""
##################################################################################################################
##########################################   NCBI Taxonomy Parser   #########################################################
##################################################################################################################

Written by: Brandon Burciaga

* Module imported by taxonomyParser.py for NCBI Taxnomy node and relationship creation.
* Holds classes TaxNamesParser, TaxNodesParser, TaxCitationsParser

"""

class TaxNamesParser(object):
    """ creates object for names.dmp """
    def __init__(self, columns):
        self.columns = columns
        self.node = "NCBI_TAXONOMY:" + columns[0].strip()
        self.term = columns[1].strip()
        self.preferred_term = columns[2].strip()

    def getPreferred(self):
        """ gets preferred term. If none available, uses name as preferred term """
        if self.preferred_term == "":
            return self.term
        return self.preferred_term

    def getSynonyms(self):
        """ adds synonyms to set, return set """
        synonymSet = set()
        synonymSet.add(self.term)
        if not self.preferred_term == "":
            synonymSet.add(self.preferred_term)
        return synonymSet