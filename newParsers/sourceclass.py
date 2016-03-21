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
                    zippedRow[header] = 'ENTREZ_GENE:' + attr
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
        Formats output header in proper way for desired attribute names to be seen in neo4j
        Adds :Label to header as well to identify node label upon database creation
        """
        with open(self.outPath, 'w') as outFile:
            fixedHeader = [None] * len(self.outHeader)
            fixHeaderDict = {'description': 'Preferred_Term', 'tax_id': 'TaxID:END_ID', 'MIM number': 'MIM_Number:END_ID',
                             'Other_tax_id': 'Other_TaxID:String[]', 'Other_GeneID': 'Other_GeneID:String[]',
                             'GO_ID': 'GO_ID:END_ID', 'PubMed': 'PubMedIDs:String[]', 'relationship': ':Type',
                             'Category': ':Type', 'Synonyms': 'Synonyms:String[]', 'ChemicalID': 'ChemicalID:END_ID',
                             'InteractionActions': ':Type', 'DiseaseID': 'DiseaeID:START_ID', 'DirectEvidence': 'DirectEvidence:String[]',
                             'InferenceGeneSymbol': 'InferenceGeneSymbol:String[]', 'OmimIDs': 'OmimIDs:String[]',
                             'PathwayID': 'PathwayID:END_ID'}
            for index, attr in enumerate(self.outHeader):
                if attr in fixHeaderDict:
                    fixedHeader[index] = fixHeaderDict[attr]
                elif attr == 'GeneID':
                    if self.file.endswith('gene_info'):
                        fixedHeader[index] = attr + ':ID'
                    else:
                        fixedHeader[index] = attr + ':START_ID'
                else:
                    fixedHeader[index] = attr
            if self.file == 'CTD_chem_gene_ixns.tsv':
                fixedHeader.extend(['Code', 'Description', 'ParentCode'])
            fixedHeader.append('Source')
            if self.file in ['mim2gene_medgen', 'CTD_genes_pathways.tsv', 'CTD_diseases_pathways.tsv']:
                fixedHeader.append(':Type')
            outFile.write(('|'.join(fixedHeader) + '\n'))

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
                    print "Could not properly read in .csv using csv.DictReader()"
        except IOError:
            print "Could not read infile in preparation for creating csv.DictReader() object"

