#!/usr/bin/python

from collections import defaultdict
from collections import OrderedDict
import importlib
import csv


class ParentClass(object):
    def __init__(self, file, source, outPath, filePath, outHeaders, fileHeader):
        self.file = file
        self.source = source
        self.outPath = outPath
        self.filePath = filePath
        self.outHeaders = outHeaders
        self.fileHeader = fileHeader

        if self.source == 'NCBIEntrezGene':
            self.NCBIEntrezGene = NCBIEntrezGene()
            print vars(self.NCBIEntrezGene)


class NCBIEntrezGene(object):
    """
    Class for parsing All_Mammalia.gene_info, All_Plants.gene_info files
    Holds logic for processing NCBI Entrez Gene nodes in preparation for writing
    """
    def __init__(self):
        self.parent = ParentClass()

        # if self.parent.file.endswith('gene_info'):
        #     self.parseGeneInfo()

    def parseGeneInfo(self):
        tsvInstance = TsvFileParser(self.parent.file, self.parent.filePath, self.outHeaders, self.fileHeader)

        for zippedRow in tsvInstance.parseTsvFile():
            synonymList = ['Symbol', 'Synonyms', 'Symbol_from_nomenclature_authority', 'Other_designations']
            self.processedRow['Synonym'] = ';'.join(self.zippedRow[x] for x in synonymList if self.zippedRow[x] != '-')
            self.processedRow['Preferred_Term'] = self.zippedRow['description']
            self.processedRow['Tax_ID'] = ("NCBI_TAXONOMY:" + self.zippedRow['tax_id'])
            return self.processedRow


class TsvFileParser(object):

    def __init__(self, file, filePath, outHeaders, fileHeader):
        self.file = file
        self.filePath = filePath
        self.outHeaders = outHeaders
        self.fileHeader = fileHeader
        self.parent = ParentClass()

    def parseTsvFile(self):
        csv.register_dialect('tabs', delimiter='\t')
        try:
            with open(self.parent.filePath, 'r') as inFile:
                try:
                    tsvReader = csv.DictReader(filter(lambda row: row[0] != '#', inFile),
                                               dialect='tabs', fieldnames=self.parent.fileHeader)
                    print 'read csv'
                    for row in tsvReader:
                        filtered = [row[i] for i in self.outHeaders]
                        zippedRow = OrderedDict(zip(self.parent.outHeaders, filtered))
                        yield zippedRow
                    print 'done with file'
                except IOError:
                    print "Could not properly read in .csv using csv.DictReader()"
        except IOError:
            print "Could not read infile in preparation for creating csv.DictReader() object"



















    # def processRow(self):
    #     """ Processes row depending on file """

    #     processedRow = defaultdict(str)

    #     processedRow['Gene_ID'] = ("ENTREZ:" + self.zippedRow['GeneID'])

    #     if self.file.endswith('gene_info'):

    #         synonymList = ['Symbol', 'Synonyms', 'Symbol_from_nomenclature_authority', 'Other_designations']
    #         processedRow['Synonym'] = ';'.join(self.zippedRow[x] for x in synonymList if self.zippedRow[x] != '-')
    #         processedRow['Preferred_Term'] = self.zippedRow['description']
    #         processedRow['Tax_ID'] = ("NCBI_TAXONOMY:" + self.zippedRow['tax_id'])
    #         return processedRow

    #     elif self.file == 'gene_group':
    #         if 'sibling' in self.zippedRow['relationship']:
    #             return None
    #         processedRow['Tax_ID'] = ("NCBI_TAXONOMY:" + self.zippedRow['tax_id'])
    #         processedRow['Relationship'] = self.zippedRow['relationship']
    #         processedRow['Other_Tax_ID'] = ("NCBI_TAXONOMY:" + self.zippedRow['Other_tax_id'])
    #         processedRow['Other_Gene_ID'] = ("ENTREZ_GENE:" + self.zippedRow['Other_GeneID'])
    #         return processedRow

    #     elif self.file == 'mim2gene_medgen':
    #         processedRow['MIM_ID'] = ("MIM:" + self.zippedRow['MIM_number'])
    #         processedRow['Source'] = self.zippedRow['Source'] if self.zippedRow['Source'] != '-' else 
    #         return processedRow

    #     elif self.file == 'gene2go':
    #         processedRow['Relationship'] = self.zippedRow['Category']
    #         processedRow['GO_ID'] = self.zippedRow['GO_ID'])
    #         return processedRow