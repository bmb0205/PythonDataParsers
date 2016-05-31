#!/usr/bin/python
import csv
from collections import defaultdict


class SourceClass(object):
    """
    SourceClass is parent class for each specific source class.
    Contains attributes passed in from main() function in refactor.py, and
    Class methods shared between the child classes for header fixing and generic tsv parsing
    """
    completeNodeSet = set()

    def __init__(self, file, source, outPath, filePath, outHeader, inputAttributes, fileHeader, ignoredAttributes):
        self.file = file
        self.source = source
        self.outPath = outPath
        self.filePath = filePath
        self.outHeader = outHeader
        self.inputAttributes = inputAttributes
        self.fileHeader = fileHeader
        self.ignoredAttributes = ignoredAttributes

    def addSourceNames(self, zippedRow):
        """ Adds capitalized source identifier string to unique source ID """
        for header, attr in zippedRow.iteritems():
            if attr:
                if header in ['GeneID', 'Other_GeneID']:
                    zippedRow[header] = 'ENTREZ:' + attr
                elif header in ['tax_id', 'Other_tax_id', 'OrganismID']:
                    zippedRow[header] = 'NCBI_TAXONOMY:' + attr
                elif header == 'MIM number':
                    zippedRow[header] = 'MIM:' + attr
        return zippedRow

    def getFullSourceName(self):
        """ Returns full name of source instead of condensed directory name """
        fullNameDict = {'NCBIEntrezGene': 'NCBI_Entrez_Gene',
                        'CTD': 'Comparative_Toxicogenomics_Database'}
        return fullNameDict[self.source]

    def writeHeader(self):
        """
        Formats output header in proper way for desired attribute names to be seen in neo4j.
        Keeps header attributes consistent throughout sources ('GO_ID' only instead of 'GO_ID' and 'GOTermID')
        Adds :Label to header as well to identify node label upon database creation
        """
        with open(self.outPath, 'w') as outFile:
            fixedHeader = [None] * len(self.outHeader)
            fixedHeaderDict = {'CTD': {'GOTermID': 'GO_ID:END_ID', 'ChemicalID': 'ChemicalID:START_ID', 'GeneID': 'GeneID:START_ID',
                                       'PathwayID': 'PathwayID:END_ID', 'InferenceGeneSymbol': 'InferenceGeneSymbol:String[]',
                                       'DiseaseID': 'DiseaseID:END_ID', 'DirectEvidence': 'DirectEvidence:String[]',
                                       'OmimIDs': 'OmimIDs:String[]', 'GeneID': 'GeneID:END_ID'},
                               'NCBIEntrezGene': {'description': 'Description', 'GeneID': 'GeneID:START_ID', 'Synonyms': 'Synonyms:String[]',
                                                  'GO_ID': 'GO_ID:END_ID', 'PubMed': 'PubMedIDs:String[]', 'tax_id': 'Tax_ID:END_ID',
                                                  'Other_tax_id': 'Other_Tax_ID:String[]', 'Other_GeneID': 'Other_GeneID:String[]',
                                                  'MIM number': 'MIM_Number:END_ID', 'Category': 'Category:Type', 'PubMed_ID': 'PubMedID:END_ID',
                                                  'relationship': 'Relationship:Type'}}

            for index, attr in enumerate(self.outHeader):
                if self.file in ['CTD_genes_pathways.tsv', 'CTD_diseases_pathways.tsv']:
                    if attr in ['GeneID', 'DiseaseID']:
                        fixedHeader[index] = attr + ':START_ID'
                    elif attr == 'PathwayID':
                        fixedHeader[index] = attr + ':END_ID'
                    else:
                        fixedHeader[index] = attr
                elif self.file in ['All_Mammalia.gene_info', 'All_Plants.gene_info']:
                    if attr == 'GeneID':
                        fixedHeader[index] = attr + ":ID"
                    elif attr in fixedHeaderDict[self.source]:
                        fixedHeader[index] = fixedHeaderDict[self.source][attr]
                else:
                    if attr in fixedHeaderDict[self.source]:
                        fixedHeader[index] = fixedHeaderDict[self.source][attr]
                    else:
                        fixedHeader[index] = attr
            fixedHeader.append('Source')
            if self.file in ['All_Mammalia.gene_info', 'All_Plants.gene_info']:
                fixedHeader.append(':Label')
            elif self.file in ['gene2pubmed', 'mim2gene_medgen']:
                fixedHeader.insert(-1, 'Relationship:Type')
            print fixedHeader
            outFile.write('|'.join(fixedHeader) + '\n')

    def parseTsvFile(self):
        """
        Register tab delimited dialect and open .tsv using csv.DictReader()
        Filter row in .tsv according to user selected attributes in .json
        Yields filteredRow from generator
        """
        csv.register_dialect('tabs', delimiter='\t')
        try:
            with open(self.filePath, 'r') as inFile:
                try:
                    tsvReader = csv.DictReader(filter(lambda row: row[0] != '#', inFile),
                                               dialect='tabs', fieldnames=self.fileHeader)
                    for row in tsvReader:
                        filteredRow = [row[i].replace('|', ';') for i in self.inputAttributes]
                        yield filteredRow  # filtered for only inputAttributes selected (synonyms and main attr)
                except IOError:
                    print "Could not properly read in .tsv using csv.DictReader()"
        except IOError:
            print "Could not read infile in preparation for creating csv.DictReader() object"

    def parseCsvFile(self):
        """
        Register comma delimited dialect and open .tsv using csv.DictReader()
        Filter row in .tsv according to user selected attributes in .json
        Yields filteredRow from generator
        """
        csv.register_dialect('commas', delimiter=',')
        try:
            with open(self.filePath, 'r') as inFile:
                try:
                    tsvReader = csv.DictReader(filter(lambda row: row[0] != '#', inFile),
                                               dialect='commas', fieldnames=self.fileHeader)
                    for row in tsvReader:
                        filteredRow = [row[i].replace('|', ';') for i in self.inputAttributes]
                        yield filteredRow  # filtered for only inputAttributes selected (synonyms and main attr)
                except IOError:
                    print "Could not properly read in .csv using csv.DictReader()"
        except IOError:
            print "Could not read infile in preparation for creating csv.DictReader() object"

