#!/usr/bin/python

import csv
import os

class FileParser(object):
    def __init__(self, source, structure):
        self.source = source
        self.structure = structure
        self.filePath = ''

        # sets fileList, sourcePath
        for key in structure.keys():
            setattr(self, key, structure[key])

        # sets appropriate headers to the files
        for file in self.fileList:
            setattr(self, file, self.fileList[file])

    def parseFile(self):
        """ """
        csv.register_dialect('tabs', delimiter='\t')
        with open(self.filePath, 'rU') as inFile:
            csvReader = csv.DictReader(filter(lambda row: row[0] != '#', inFile),
                                       dialect='tabs', fieldnames=self.fileList[self.file])
            for row in csvReader:
                yield row

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