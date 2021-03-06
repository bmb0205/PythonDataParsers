#!/usr/bin/python

import re

"""
##################################################################################################################
##########################################   Ontology Parser Classes  #########################################################
##################################################################################################################

Written by: Brandon Burciaga
* Module imported by ontologyParser.py for various ontology node and relationship creation.
* Holds class OntologyParser
"""


class OntologyParser(object):
    """
    Class OntologyParser holds an ontology object for processing.
    Input data type: dictionary from individual ontology stanza

    """
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def skipObsolete(self):
        """ Skips obsolete terms """
        if "is_obsolete" in self.kwargs:
            return True

    def getName(self):
        """ Returns name """
        if "name" in self.kwargs:
            name = self.kwargs["name"][0]
            return name

    def getID(self):
        """ Returns ID """
        if "id" in self.kwargs:
            ID = self.kwargs["id"][0]
            return ID

    def getDef(self):
        """ Trimms definition and returns it """
        if "def" in self.kwargs:
            temp = self.kwargs["def"][0]
            trimmed = re.split(" \[", temp)[0]
            return trimmed

    def getSynonyms(self):
        """ Parses synonyms and xrefs and joins into ; separated string of synonyms """
        synonymSet = set()
        if "synonym" not in self.kwargs:
            return ""
        if "synonym" in self.kwargs:
            for synonym in self.kwargs["synonym"]:
                if "EXACT" in synonym:
                    synonym = re.split(" EXACT ", synonym)[0]
                    synonymSet.add(synonym)
        if "xref" in self.kwargs:
            for xref in self.kwargs["xref"]:
                synonymSet.add(xref)
        synonymSet = ";".join(synonymSet)
        synonymSet = synonymSet.replace('"', "").replace("'", "")
        return synonymSet

    def getRelationships(self):
        """
        Gathers relationships according to key (is_a, relationship, intersection_of) and returns in set
        Skips anonymous chemicals, PATO relns and uses either specific or hard coded predicate depending on format
        """
        relationSet = set()
        ID = self.kwargs["id"][0]
        if "is_a" in self.kwargs:
            for reln in self.kwargs["is_a"]:
                predicate = "is_a"
                if reln.startswith("PATO"):
                    continue
                if reln.startswith("TO"):
                    if "is_inferred" in reln:
                        subject = reln.split(" ")[0]
                    else:
                        subject = reln.split(" ! ")[0]
                    relationship = (ID, predicate, subject)
                    relationSet.add(relationship)
                subject = reln.split(" ! ")[0]
                relationship = (ID, predicate, subject)
                relationSet.add(relationship)
        if "relationship" in self.kwargs:
            for reln in self.kwargs["relationship"]:
                predicate = reln.split(" ")[0]
                reln = reln.split(" ")[1]
                if predicate.startswith("OBO_REL"):
                    predicate = predicate.split(":")[1]
                relationship = (ID, predicate, reln)
                relationSet.add(relationship)
        if "intersection_of" in self.kwargs:
            for intersect in self.kwargs["intersection_of"]:
                if intersect.startswith("PATO"):
                    continue
                intersect = intersect.split(" ")
                test = intersect[0]
                if "anon_chemical" in intersect[1]:
                    continue
                if test[0].islower():  # use specific predicate
                    predicate = test
                    subject = intersect[1]
                    relationship = (ID, predicate, subject)
                    relationSet.add(relationship)
                else:
                    predicate = "intersect_of"
                    subject = intersect[0]
                    if subject.startswith("OBO_REL"):
                        predicate = subject.split(":")[1]
                        subject = intersect[1]
                    relationship = (ID, predicate, subject)
                    relationSet.add(relationship)
        return relationSet

    def getLabel(self):
        """ Hard codes label according to source """
        label = ""
        ID = self.kwargs["id"][0]
        if ID.startswith("GO"):
            label = "Gene"
        elif ID.startswith("CHEBI"):
            label = "Chemical"
        elif ID.startswith("DOID"):
            label = "Disease"
        elif ID.startswith("PO") or ID.startswith("TO"):
            label = "Plant"
        elif ID.startswith("MP") or ID.startswith("HP"):
            label = "Phenotype"
        elif ID.startswith("ExO"):
            label = "Disease_Exposure"
        elif ID.startswith("MESH"):
            label = "Medical_Heading"
        return label
