#!/usr/bin/python

from collections import defaultdict
from collections import OrderedDict
import importlib
import locale
import csv
import time


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

    def addSourceNames(self, zippedRow):
        """ Adds capitalized source identifier string to unique source ID """
        for header, attr in zippedRow.iteritems():
            if header in ['GeneID', 'Other_GeneID']:
                zippedRow[header] = 'ENTREZ_GENE:' + attr
            elif header in ['tax_id', 'Other_tax_id']:
                zippedRow[header] = 'NCBI_TAXONOMY:' + attr
            elif header == 'MIM number':
                zippedRow[header] = 'MIM:' + attr
        return zippedRow

    def getFullSourceName(self):
        """ Returns full name of source instead of condensed directory name """
        fullNameDict = {'NCBIEntrezGene': 'NCBI_Entrez_Gene',
                        'CTD': 'Comparative_Toxicogenomics_Database'}
        return fullNameDict[self.source]

    def fixHeader(self, outFile):
        """
        Formats output header in proper way for desired attribute names to be seen in neo4j
        Adds :Label to header as well to identify node label upon database creation
        """
        fixedHeader = self.outHeader
        oldHeader = self.outHeader
        print 'start'
        print self.outHeader
        print fixedHeader
        fixHeaderDict = {'description': 'Preferred_Term', 'tax_id': 'TaxID:END_ID', 'MIM number': 'MIM_Number:END_ID',
                         'Other_tax_id': 'Other_TaxID:String[]', 'Other_GeneID': 'Other_GeneID:String[]',
                         'GO_ID': 'GO_ID:END_ID', 'PubMed': 'PubMedIDs:String[]', 'relationship': ':Type',
                         'Category': ':Type', 'Synonyms': 'Synonyms:String[]'}
        for index, attr in enumerate(self.outHeader):
            if attr in fixHeaderDict:
                fixedHeader[index] = fixHeaderDict[attr]
            elif attr == 'GeneID':
                if self.file.endswith('gene_info'):
                    fixedHeader[index] = attr + ':ID'
                else:
                    fixedHeader[index] = attr + ':START_ID'
        fixedHeader.append('Source')
        if self.file == 'mim2gene_medgen':
            fixedHeader.append(':Type')
        print 'end'
        print self.outHeader
        print fixedHeader
        print oldHeader
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


class NCBIEntrezGene(SourceClass):
    """
    Class for parsing All_Mammalia.gene_info, All_Plants.gene_info files
    Holds logic for processing NCBI Entrez Gene nodes in preparation for writing
    """
    print "\n~~~~~ Parsing NCBI Entrez Gene database ~~~~~\n"
    completeNodeSet = set()
    def checkFile(self):

        # if self.file.endswith('gene_info'):
        #     nodeSet = self.parseGeneInfo()
        #     completeNodeSet.update(nodeSet)

        # elif self.file.endswith('gene2go'):
        #     self.parseGene2GO()

        # elif self.file.endswith('gene_group'):
        #     self.parseGeneGroup()

        if self.file.endswith('mim2gene_medgen'):
            self.parseMIM2Gene()

    def parseGeneInfo(self):
        """ """
        start = time.clock()
        nodeCount = 0
        nodeSet = set()
        print "Parsing %s\n" % self.filePath
        with open(self.outPath, 'w') as outFile:
            self.fixHeader(outFile)
            # outFile.write('|'.join(fixedHeader) + '\n')
            for outString, nodeID in self.processNodeInfo():
                nodeCount += 1
                nodeSet.add(nodeID)
                outFile.write(outString + '\n')
        end = time.clock()
        duration = end - start
        print "\n\tIt took %s seconds to parse %s\n" % (duration, self.filePath)
        print '\t%s ENTREZ Gene nodes have been created.\n' % locale.format('%d', nodeCount, True)
        return nodeSet

    def parseMIM2Gene(self):
        start = time.clock()
        print "Parsing %s\n" % self.filePath
        with open(self.outPath, 'w') as outFile:
            self.fixHeader(outFile)
            # outFile.write('|'.join(self.fixHeader()) + '\n')
            self.processRelationshipInfo()

    def parseGeneGroup(self):
        start = time.clock()
        relnCount = 0
        relnDict = self.processRelationshipInfo()
        print "Parsing %s\n" % self.filePath
        with open(self.outPath, 'w') as outFile:
            self.fixHeader(outFile)
            # outFile.write('|'.join(fixedHeader) + '\n')
            for relnTup, alternateIDs in relnDict.iteritems():
                relnCount += 1
                relnList = list(relnTup)
                altGeneIDs = ';'.join(alternateIDs['Other_GeneID'])
                altTaxIDs = ';'.join(alternateIDs['Other_tax_id'])
                outFile.write('|'.join(relnList) + "|" + altGeneIDs + '|' + altTaxIDs + '|' + self.getFullSourceName() + '\n')
        end = time.clock()
        duration = end - start
        print "\n\tIt took %s seconds to parse %s\n" % (duration, self.filePath)
        print '\t%s ENTREZ Gene to NCBI Taxonomy relationships have been created.\n' % locale.format('%d', relnCount, True)

    def parseGene2GO(self):
        """ """
        start = time.clock()
        relnCount = 0
        print "Parsing %s\n" % self.filePath
        with open(self.outPath, 'w') as outFile:
            relnDict = self.processRelationshipInfo()
            self.fixHeader(outFile)
            # outFile.write('|'.join(fixedHeader) + '\n')
            for relnTup, idSet in relnDict.iteritems():
                relnCount += 1
                fullIDList = ';'.join([medID for medID in idSet])
                relnList = list(relnTup)
                relnList.insert(-1, fullIDList)
                relnList.append(self.getFullSourceName())
                outString = '|'.join(relnList)
                outFile.write(outString + '\n')
        end = time.clock()
        duration = end - start
        print "\n\tIt took %s seconds to parse %s\n" % (duration, self.filePath)
        print '\t%s ENTREZ Gene to Gene Ontology relationships have been created.\n' % locale.format('%d', relnCount, True)

    def getPredicate(self, predicate):
        """ Hard codes text as string according to the disorder's phene mapping key. """
        predicateOptions = {'Component': 'is_a',
                            'Function': 'performs',
                            'Process': 'part_of'}
        if predicate in predicateOptions:
            return predicateOptions[predicate]
        else:
            return ""

    def processRelationshipInfo(self):
        """
        Processes filteredRow which is yielded from self.parseTsvFIle().
        Returns defaultdict with (tax_id, relationship, geneID) as
        composite key for aggregated pubmed IDs
        """
        if self.file == 'gene2go':
            relnDict = defaultdict(set)
            for filteredRow in self.parseTsvFile():
                zippedRow = OrderedDict(zip(self.outHeader, filteredRow))
                zippedRow = self.addSourceNames(zippedRow)
                relnTuple = (zippedRow['GeneID'], zippedRow['GO_ID'], self.getPredicate(zippedRow['Category']))
                relnDict[relnTuple].update([medID for medID in zippedRow['PubMed'].split(';') if medID != '-'])
            return relnDict

        elif self.file == 'gene_group':
            relnDict = defaultdict(lambda: defaultdict(set))
            for filteredRow in self.parseTsvFile():
                zippedRow = OrderedDict(zip(self.outHeader, filteredRow))
                zippedRow = self.addSourceNames(zippedRow)
                relnTup = (zippedRow['tax_id'], zippedRow['GeneID'], zippedRow['relationship'])
                relnDict[relnTup]['Other_GeneID'].add(zippedRow['Other_GeneID'])
                relnDict[relnTup]['Other_tax_ID'].add(zippedRow['Other_tax_id'])
            return relnDict

        elif self.file == 'mim2gene_medgen':
            for filteredRow in self.parseTsvFile():
                zippedRow = OrderedDict(zip(self.outHeader, filteredRow))
                if zippedRow['GeneID'] != '-':
                    zippedRow = self.addSourceNames(zippedRow)
                    outString = ('|'.join(zippedRow.values()) + '|' + self.getFullSourceName() + '|' + 'belongs_to')
                    print outString



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
            tempList.insert(self.outHeader.index('Synonyms:String[]'), synonyms)
            tempList.append(self.getFullSourceName())
            tempList[0] = 'ENTREZ_GENE:' + tempList[0]
            outString = '|'.join(tempList)
            yield outString, tempList[0]


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
