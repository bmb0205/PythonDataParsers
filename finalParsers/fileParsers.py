#!/usr/bin/python

import csv
import os
import pprint
from collections import OrderedDict
from collections import defaultdict
import time


class CsvFileParser():

    def __init__(self, file, source, outPath, filePath, outHeaders, fileHeader):
        self.file = file
        self.source = source
        self.outPath = outPath
        self.filePath = filePath
        self.outHeaders = outHeaders
        self.fileHeader = fileHeader

    def getClass(self):
        print 'getting class...'
        instance = self.source
        print instance

    def parseCsvFile(self):
        print "FUUUCK"
        csv.register_dialect('tabs', delimiter='\t')
        print 'rrrr'
        try:
            print 'trying...'
            with open(self.filePath, 'r') as inFile:
                print 'opened infile'
                try:
                    csvReader = csv.DictReader(filter(lambda row: row[0] != '#', inFile),
                                               dialect='tabs', fieldnames=self.fileHeader)
                    print 'read csv'
                    if self.source == "NCBIEntrezGene":
                        print '\n\nlol', self.file
                        for row in csvReader:
                            filtered = [row[i] for i in self.outHeaders]
                            zippedRow = OrderedDict(zip(self.outHeaders, filtered))

                            """
                            here...3am. figure out how to pick which class to instantiate
                            based on source vs hardcoding

                            """
                            sourceInstance = self.getClass()
                            # sourceInstance = self.source(zippedRow)
                            processedRow = sourceInstance.processRow()
                            yield processedRow
                        print 'done with file'
                except IOError:
                    print "Could not properly read in .csv using csv.DictReader()"
        except IOError:
            print "Could not read infile in preparation for creating csv.DictReader() object

class NCBIEntrezGene(object):
    """
    Class for parsing All_Mammalia.gene_info, All_Plants.gene_info files
    Processes NCBI Entrez Gene nodes in preparation for writing
    """
    def __init__(self, zippedRow):
        self.zippedRow = zippedRow

    def processRow(self):
        processedRow = defaultdict(str)
        synonymList = ['Symbol', 'Synonyms', 'Symbol_from_nomenclature_authority', 'Other_designations']
        processedRow['Synonym'] = ';'.join(self.zippedRow[x] for x in synonymList if self.zippedRow[x] != '-')
        processedRow['Preferred_Term'] = self.zippedRow['description']
        processedRow['Gene_ID'] = ("ENTREZ_GENE:" + self.zippedRow['GeneID'])
        processedRow['Tax_ID'] = ("NCBI_TAXONOMY:" + self.zippedRow['tax_id'])
        return processedRow
