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

        # if self.parent.file == 'CTD_chem_gene_ixn_types.tsv':
        #     self.getChemGeneTypes()

        # elif self.parent.file == 'CTD_chem_gene_ixns.tsv':
        #     # self.parent.outHeader  # adds propery headers from CTD_chem_gene_ixn_types.tsv
        #     self.parent.writeHeader()
        #     self.writeChemGeneRelationships()

        # if self.parent.file == 'CTD_chemicals_diseases.tsv':
        #     self.parent.writeHeader()
        #     self.writeChemDiseaseRelationships()

        # if self.parent.file == 'CTD_genes_pathways.tsv':
        #     self.parent.writeHeader()
        #     self.writeGenePathwayRelationships()

        # if self.parent.file == 'CTD_diseases_pathways.tsv':
        #     self.parent.writeHeader()
        #     self.writeDiseasePathwayRelationships()

        if self.parent.file == 'CTD_chem_pathways_enriched.tsv':
            self.parent.writeHeader()
            self.writeChemPat

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
                                           typeDict[typeName]['Code'], typeDict[typeName]['Description'],
                                           typeDict[typeName]['ParentCode'], self.parent.getFullSourceName()))
                    outFile.write(relnString + '\n')
            end = time.clock()
            print 'time: ', end - start

    def writeChemDiseaseRelationships(self):
        """ """
        with open(self.parent.outPath, 'a') as outFile:
            relnDict = self.processRelationshipInfo()
            for relnTup, nodeInfo in relnDict.iteritems():
                # joinedInfo = '|'.join(';'.join(info) for header, info in nodeInfo.iteritems())
                outString = '|'.join(('|'.join(relnTup), ';'.join(nodeInfo['DirectEvidence']),
                                      ';'.join(nodeInfo['InferenceGeneSymbol']), ';'.join(nodeInfo['InferenceScore']),
                                      ';'.join(nodeInfo['OmimIDs']), 'associated_with', self.parent.getFullSourceName()))
                outFile.write(outString + '\n')

    def writeGenePathwayRelationships(self):
        """ """
        with open(self.parent.outPath, 'a') as outFile:
            for filteredRow in self.parent.parseTsvFile():
                zippedRow = self.addSourceNames(OrderedDict(zip(self.parent.outHeader, filteredRow)))
                outString = '|'.join(zippedRow.values()) + '|' + self.parent.getFullSourceName() + '|involved_in'
                outFile.write(outString + '\n')

    def writeDiseasePathwayRelationships(self):
        """ """
        with open(self.parent.outPath, 'a') as outFile:
            relnDict = self.processRelationshipInfo()
            for relnTup, nodeInfo in relnDict.iteritems():
                outString = ('|'.join(relnTup) + '|' + ';'.join(nodeInfo['InferenceGeneSymbol']) +
                             '|' + self.parent.getFullSourceName() + '|involved_in')
                outFile.write(outString + '\n')

    def processRelationshipInfo(self):
        """ """
        relnDict = defaultdict(lambda: defaultdict(set))
        if self.parent.file == 'CTD_chemicals_diseases.tsv':
            for filteredRow in self.parent.parseTsvFile():
                zippedRow = self.addSourceNames(OrderedDict(zip(self.parent.outHeader, filteredRow)))
                relnTup = (zippedRow['ChemicalID'], zippedRow['DiseaseID'])
                for header, attr in zippedRow.iteritems():
                    if header not in ['DiseaseID', 'ChemicalID']:
                        if attr:
                            relnDict[relnTup][header].add(attr)
            return relnDict

        elif self.parent.file == 'CTD_diseases_pathways.tsv':
            for filteredRow in self.parent.parseTsvFile():
                zippedRow = self.addSourceNames(OrderedDict(zip(self.parent.outHeader, filteredRow)))
                relnTup = (zippedRow['DiseaseID'], zippedRow['PathwayID'])
                for header, attr in zippedRow.iteritems():
                    if header not in ['DiseaseID', 'PathwayID', 'PathwayName', 'DiseaseName']:
                        if attr:
                            relnDict[relnTup][header].add(attr)
            return relnDict










