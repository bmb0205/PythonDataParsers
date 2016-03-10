#!/usr/bin/python

import csv
from collections import OrderedDict
import importlib


class TsvFileParser(object):

    def __init__(self, file, filePath, outHeaders, fileHeader):
        self.file = file
        self.filePath = filePath
        self.outHeaders = outHeaders
        self.fileHeader = fileHeader

    def parseTsvFile(self):
        csv.register_dialect('tabs', delimiter='\t')
        try:
            with open(self.filePath, 'r') as inFile:
                try:
                    tsvReader = csv.DictReader(filter(lambda row: row[0] != '#', inFile),
                                               dialect='tabs', fieldnames=self.fileHeader)
                    print 'read csv'
                    for row in tsvReader:
                        filtered = [row[i] for i in self.outHeaders]
                        zippedRow = OrderedDict(zip(self.outHeaders, filtered))
                        yield zippedRow
                    print 'done with file'
                except IOError:
                    print "Could not properly read in .csv using csv.DictReader()"
        except IOError:
            print "Could not read infile in preparation for creating csv.DictReader() object"


"""
Okay so.....don;t use this to call the classes...uses the classes to call this and get rid of checks here.
This should be automated and easy where you don't need to look at it alongside other scripts
"""