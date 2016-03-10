#!/usr/bin/python

import csv
import os
import pprint
from collections import OrderedDict
from collections import defaultdict
import time
import importlib

class CsvFileParser():

    def __init__(self, file, source, outPath, filePath, outHeaders, fileHeader):
        self.file = file
        self.source = source
        self.outPath = outPath
        self.filePath = filePath
        self.outHeaders = outHeaders
        self.fileHeader = fileHeader

    def parseCsvFile(self):
        csv.register_dialect('tabs', delimiter='\t')
        try:
            with open(self.filePath, 'r') as inFile:
                try:
                    csvReader = csv.DictReader(filter(lambda row: row[0] != '#', inFile),
                                               dialect='tabs', fieldnames=self.fileHeader)
                    print 'read csv'
                    if self.source == "NCBIEntrezGene":
                        for row in csvReader:
                            filtered = [row[i] for i in self.outHeaders]
                            zippedRow = OrderedDict(zip(self.outHeaders, filtered))

                            module = importlib.import_module('sourceClasses')
                            myClass = getattr(module, self.source)

                            sourceInstance = myClass(zippedRow, self.file)
                            processedRow = sourceInstance.processRow()
                            if processedRow:
                                yield processedRow
                        print 'done with file'
                except IOError:
                    print "Could not properly read in .csv using csv.DictReader()"
        except IOError:
            print "Could not read infile in preparation for creating csv.DictReader() object"
