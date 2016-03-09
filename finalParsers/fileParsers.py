#!/usr/bin/python

import csv
import os
import pandas
import StringIO

class CsvFileParser(object):
    def __init__(self, file, outPath, filePath, outHeaders, fileHeader):
        self.file = file
        self.outPath = outPath
        self.filePath = filePath
        self.outHeaders = outHeaders
        self.fileHeader = fileHeader

    def parseCsv(self):
        """ """
        # csv.register_dialect('tabs', delimiter='\t')
        with open(self.filePath, 'r') as inFile:
            data = pandas.read_csv(inFile, sep='\t', comment='#', names=self.fileHeader)
            # thing = data.groupby('GeneID')
            # print thing.values
            grouped = data.groupby('GeneID')['Synonyms'].apply(set)
            print grouped[:10]

            # csvReader = csv.DictReader(filter(lambda row: row[0] != '#', inFile),
            #                            dialect='tabs', fieldnames=self.fileList[self.file])
            # for row in csvReader:
            #     yield row

    def writeRelationships(self):
        """ """
        print self.file, '\t', self.fileList[self.file]
        # for row in FileParser.parseFile(self):
        #     csvWriter = csv.DictWriter(self.outPath, fieldnames = )



    # def parseFile(self):
    #     """ """
    #     for file in self.fileList.keys():
    #         filePath = os.path.join(self.sourcePath, file)
    #         csv.register_dialect('tabs', delimiter='\t')
    #         with open(filePath, 'rU') as inFile:
    #             for line in inFile:
    #                 if line.startswith('#'):
    #                     continue
    #                 break
    #             csvReader = csv.DictReader(inFile, dialect='tabs', fieldnames=self.fileList[file])
    #             for row in csvReader:
                    # yield row