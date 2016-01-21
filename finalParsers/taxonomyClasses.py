#!/usr/bin/python

"""
##################################################################################################################
##########################################   NCBI Taxonomy Parser   #########################################################
##################################################################################################################

Module imported by taxonomyParser.py for NCBI Taxnomy node and relationship creation.
Holds classes TaxNamesParser, TaxNodesParser, TaxCitationsParser

"""

class TaxNamesParser(object):
    """ creates object for names.dmp """
    def __init__(self, columns):
        self.columns = columns
        self.node = "NCBI_TAXONOMY:" + columns[0].strip()
        self.term = columns[1].strip()
        self.preferred_term = columns[2].strip()
        self.synonyms = set()

    def getPreferred(self):
        """ gets preferred term. If none available, uses name as preferred term """
        if self.preferred_term == "":
            self.preferred_term = self.term;
            return self.preferred_term
        return self.preferred_term

    def getSynonyms(self):
        """ adds synonyms to set, return set """
        self.synonyms.add(self.term)
        if self.preferred_term != "":
            self.synonyms.add(self.preferred_term)
        return self.synonyms


class TaxNodesParser(object):
    """ creates object for nodes.dmp """
    def __init__(self, columns):
        self.columns = columns
        self.node = "NCBI_TAXONOMY:" + self.columns[0].strip()
        self.parent = "NCBI_TAXONOMY:" + self.columns[1].strip()
        self.rank = self.columns[2].strip()


class TaxCitationsParser(object):
    """ creates object for citations.dmp """
    def __init__(self, columns):
        self.columns = columns
        self.nodeList = self.columns[-2].strip().split(" ")
        self.medline_id = self.columns[3].strip()