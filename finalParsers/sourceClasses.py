#!/usr/bin/python

from collections import defaultdict
from collections import OrderedDict
import importlib
import csv


class SourceClass(object):
    """
    SourceClass is parent class for each specific source class.
    Contains attributes passed in from main() function in refactor.py, and
    Class methods shared between the child classes for header fixing and generic tsv parsing
    """
    def __init__(self, file, source, outPath, filePath, outHeader, inputAttributes, fileHeader, ignoredAttributes):
        self.file = file
        self.source = source
        self.outPath = outPath
        self.filePath = filePath
        self.outHeader = outHeader
        self.inputAttributes = inputAttributes
        self.fileHeader = fileHeader
        self.ignoredAttributes = ignoredAttributes

    def fixHeader(self, attribute):
        """
        Formats output header in proper way for desired attribute names to be seen in neo4j
        Adds :Label to header as well to identify node label upon database creation
        """
        replaceDict = {'description': 'Preferred_Term'}
        fixedIndex = self.outHeader.index(attribute)
        self.outHeader[fixedIndex] = replaceDict[attribute]
        fixedHeader = self.outHeader
        fixedHeader.append(':Label')
        return fixedHeader

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
                        # maybe clean the items here to remove '|' etc
                        filteredRow = [row[i].replace('|', ';') for i in self.inputAttributes]
                        yield filteredRow  # filtered for only inputAttributes selected (synonyms and main attr)
                    print 'done with file'
                except IOError:
                    print "Could not properly read in .csv using csv.DictReader()"
        except IOError:
            print "Could not read infile in preparation for creating csv.DictReader() object"


class NCBIEntrezGene(SourceClass):
    """
    Class for parsing All_Mammalia.gene_info, All_Plants.gene_info files
    Holds logic for processing NCBI Entrez Gene nodes in preparation for writing
    """
    def checkFile(self):
        if self.file.endswith('gene_info'):
            with open(self.outPath, 'w') as outFile:
                tempHeader = self.fixHeader('description')
                fixedHeader = '|'.join([(attr + ':String[]') if attr == 'Synonyms' else attr for attr in tempHeader])
                outFile.write(fixedHeader + '\n')
                for outString in self.processNodeInfo():
                    outFile.write(outString + '\n')
        # elif self.file.endswith('gene2go'):
        #     continue

    def processNodeInfo(self):
        """
        Processes row yielded from parseTsvFile() generator function
        Gathers synonyms based on user selection in .json
        Uses list comprehension to create and alter outString for node writing to out file
        """
        for filteredRow in self.parseTsvFile():
            ignoredIndexList = [i for i, n in enumerate(self.inputAttributes) if n in self.ignoredAttributes]
            syndexList = [index for index, attr in enumerate(self.inputAttributes) if attr.lower() in ['synonym', 'synonyms']]
            ignoredIndexList.extend(syndexList)
            tempList = [n for i, n in enumerate(filteredRow) if i not in ignoredIndexList and n != '-']
            synonyms = ";".join([filteredRow[i] for i in ignoredIndexList if filteredRow[i] != '-'])
            tempList.insert(self.outHeader.index('Synonyms'), synonyms)
            tempList.append(self.source)
            tempList[0] = 'ENTREZ_GENE:' + tempList[0]
            outString = '|'.join(tempList)
            yield outString


# class CTD(SourceClass):
#     """
#     Does a thing
#     """
#     # def __init__()

#     def checkFile(self):
#         if self.file.endswith(''):
#             self.processNodeInfo()

#     def parseGeneInfo(self):
#         tsvInstance = TsvFileParser()

#         for zippedRow in tsvInstance.parseTsvFile():
#             synonymList = ['Symbol', 'Synonyms', 'Symbol_from_nomenclature_authority', 'Other_designations']
#             self.processedRow['Synonym'] = ';'.join(self.zippedRow[x] for x in synonymList if self.zippedRow[x] != '-')
#             self.processedRow['Preferred_Term'] = self.zippedRow['description']
#             self.processedRow['Tax_ID'] = ("NCBI_TAXONOMY:" + self.zippedRow['tax_id'])
#             return self.processedRow
