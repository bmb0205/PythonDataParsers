#!/usr/bin/python

from collections import defaultdict
from collections import OrderedDict
import locale
import time
from sourceclass import SourceClass

typeDict = defaultdict(dict)
chemGeneHeader = list()


class CTD(SourceClass):
    """
    Does a thing
    """
    def __init__(self, file, source, outPath, filePath, outHeader,
                 inputAttributes, fileHeader, ignoredAttributes):
        self.parent = SourceClass(file, source, outPath, filePath, outHeader,
                                  inputAttributes, fileHeader, ignoredAttributes)

    def checkFile(self):

        if self.parent.file == 'CTD_chem_gene_ixn_types.tsv':
            self.getChemGeneTypes()
            chemGeneHeader = self.parent.outHeader
            print 'here', chemGeneHeader

        elif self.parent.file == 'CTD_chem_gene_ixns.tsv':
            # self.parent.outHeader  # adds propery headers from CTD_chem_gene_ixn_types.tsv
            self.parent.writeHeader()
            self.writeChemGeneRelationships()

        # elif self.parent.file.endswith('gene2go'):
        #     self.parent.writeHeader()
        #     self.writeGeneToGOrelationships()

        # elif self.parent.file.endswith('gene_group'):
        #     self.parent.writeHeader()
        #     self.writeGeneToTaxonomyRelationships()

        # elif self.parent.file.endswith('mim2gene_medgen'):
        #     self.parent.writeHeader()
        #     self.writeGeneToMIMrelationships()

    # def writeChemGeneRelationships(self, typeDict):
    #     with open(self.parent

    def getChemGeneTypes(self):
        """ """
        for filteredRow in self.parent.parseTsvFile():
            zippedRow = OrderedDict(zip(self.parent.outHeader, filteredRow))
            typeDict[zippedRow['TypeName']]
            for header, attr in zippedRow.iteritems():
                if header != 'TypeName':
                    typeDict[zippedRow['TypeName']][header] = attr

    def writeChemGeneRelationships(self):
        """ """
        with open(self.parent.outPath, 'a') as outFile:
            start = time.clock()
            for filteredRow in self.parent.parseTsvFile():
                zippedRow = self.addSourceNames(OrderedDict(zip(self.parent.outHeader, filteredRow)))
                zippedRow['InteractionActions'] = zippedRow['InteractionActions'].replace('^', '_').split(';')
                for action in zippedRow['InteractionActions']:
                    typeName = action.split('_')[1]
                    relnString = '|'.join((zippedRow['ChemicalID'], zippedRow['GeneID'], zippedRow['Organism'],
                                           zippedRow['OrganismID'], zippedRow['Interaction'], action, zippedRow['PubMedIDs'],
                                           action, typeDict[typeName]['Code'], typeDict[typeName]['Description'],
                                           typeDict[typeName]['ParentCode'], self.parent.getFullSourceName()))
                    outFile.write(relnString + '\n')
            end = time.clock()
            print 'time: ', end - start


















