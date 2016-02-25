#!/usr/bin/python

import re

"""
##################################################################################################################
##########################################   OMIM  #########################################################
##################################################################################################################

Written by: Brandon Burciaga

* Module imported by omimParser.py for OMIM node and relationship creation.
* Holds classes MIMNode, DisorderNode and getDisorderNodeInfo() method
"""


class MIMNode(object):
    """ Populates object with attributes from geneMap2.txt file for node creation """
    def __init__(self, columns):
        self.columns = columns
        self.cytogenetic_location = columns[4].strip()
        self.gene_symbol = columns[5].strip()
        self.name = columns[7].strip()
        self.gene_id = "OMIM:" + columns[8].strip()
        self.disorder_info = columns[11].strip()

    def getGeneSymbols(self):
        """ Clean gene symbols, return empty strin if gene symbol is None """
        if "," in self.gene_symbol:
            symbols = self.gene_symbol.replace(", ", ";")
            return symbols
        else:
            if self.gene_symbol is None:
                return self.gene_symbol
            else:
                return ""

    def getDisorderInfo(self):
        """
        Uses regular expressions to parse and manipulate disorder information for each node
        Conditionals take into account OMIM errors with this data version, as well as number of
            disorders, missing phene keys or disorder MIMs.
        Returns a set of relationships for this gene MIM after being cleaned.
        """
        splitter = "\(\d\); "
        found_id = "\d{6}"
        found = re.search(splitter, self.disorder_info)
        relnSet = set()
        disorderMIM = ''
        if found:  # multiple associated disorders
            disorders = re.split("; ", self.disorder_info)
            for dis in disorders:
                split = dis.rsplit(" ", 2)
                hasID = re.search(found_id, split[1])

                if not hasID:  # multiple disorders, one missing disorder MIM, so gene MIM == disorder/phene MIM + 'p'
                    if ")" not in split[-1]:  # missing phene key in this one instance, due to OMIM error. Hardcode "(3)"
                        disorderMIM = "OMIM:" + split[-1]
                        relnSet.add((self.gene_id, "3", disorderMIM))
                    else:
                        disorderMIM = self.gene_id + "p"
                        pheneKey = split[-1][1:-1]
                        relnSet.add((self.gene_id, pheneKey, disorderMIM))
                else:  # multiple disorders, has disorder/phene MIM available
                    disorderMIM = "OMIM:" + split[1]
                    if len(disorderMIM) > 10:  # commas after disorder MIM in two instances, 273300, 167400
                        disorderMIM = disorderMIM.rstrip(',')
                    pheneKey = split[2][1:-1]
                    relnSet.add((self.gene_id, pheneKey, disorderMIM))

        else:  # one disorder
            found = re.search(found_id, self.disorder_info)
            split = self.disorder_info.rsplit(" ", 2)
            if found:  # contain disorder MIMs
                disorderMIM = "OMIM:" + split[1]
                pheneKey = split[2][1:-1]
                relnSet.add((self.gene_id, pheneKey, disorderMIM))
            else:  # does not contain disorder MIMs
                disorderMIM = self.gene_id + 'p'
                pheneKey = split[-1][1:-1]
                relnSet.add((self.gene_id, pheneKey, disorderMIM))
        return relnSet


class DisorderNode(object):
    """ Class holds attributes for disorder node object """
    def __init__(self, columns):
        self.columns = columns
        self.geneMIM = "OMIM:" + columns[2].strip()
        self.disorderInfo = getDisorderNodeInfo(columns[0].strip(), self.geneMIM)
        self.text = self.disorderInfo[0].rstrip(',')
        self.pheneKey = self.disorderInfo[-1][1:-1].strip()
        self.disorderID = self.disorderInfo[1].strip()

    def setDisorderID(self):
        """ returns disorderID + 'p' in case where disorderID = gene """
        self.disorderID = self.disorderID + 'p'


def getDisorderNodeInfo(disorder, geneMIM):
    """
    Searches for disorder MIM for disorder MIM node.
    Uses gene MIM if not found. Returns tuple of text, MIM and phene key
    Used as basis for attribute creation in DisorderNode class above
    """
    found_id = "\d{6}"
    disorderInfo = ""
    found = re.search(found_id, disorder)
    split = disorder.rsplit(" ", 2)
    if found:  # contain disorder MIMs
        if ")" not in split[-1]:  # missing phene key in this one instance, due to OMIM error. Hardcode "(3)"
            disorderInfo = ((" ".join(split[:2])), ("OMIM:" + split[-1]), "(3)")
        else:
            if split[1].endswith(','):  # 273300, 167400, commas not supposed to be there: OMIM error
                disorderInfo = (split[0], ("OMIM:" + split[1].rstrip(',')), split[2])
            else:
                disorderInfo = (split[0], ("OMIM:" + split[1]), split[2])
    else:  # does not contain disorder MIMs, use gene MIM + 'p'
        disorderInfo = ((split[0] + " " + split[1]), (geneMIM + "p"), split[-1])
    return disorderInfo




