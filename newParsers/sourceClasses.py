#!/usr/bin/python

from collections import defaultdict
from collections import OrderedDict
import importlib
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

    def fixHeader(self):
        """
        Formats output header in proper way for desired attribute names to be seen in neo4j
        Adds :Label to header as well to identify node label upon database creation
        """
        replaceDict = {'description': 'Preferred_Term', 'tax_id': 'TaxID',
                       'Other_tax_id': 'Other_TaxID', 'relationship': ':Type', 'Category': ':Type'}
        print self.outHeader
        fixedHeader = self.outHeader
        for index, attr in enumerate(self.outHeader):
            if attr == 'GeneID':
                fixedHeader[index] = attr + ':START_ID'
            elif attr == 'GO_ID':
                fixedHeader[index] = attr + ':END_ID'
            elif attr == 'tax_id':
                fixedHeader[index] = replaceDict[attr] + ':END_ID'
            elif attr in replaceDict:
                self.outHeader[index] = replaceDict[attr]
                fixedHeader = self.outHeader
        fixedHeader.append('Source')
        print fixedHeader
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
        print "\n~~~~~ Parsing NCBI Entrez Gene database ~~~~~\n"

        if self.file.endswith('gene_info'):
            start = time.clock()
            print "Parsing %s\n" % self.filePath
            with open(self.outPath, 'w') as outFile:
                tempHeader = self.fixHeader()
                fixedHeader = '|'.join([(attr + ':String[]') if attr == 'Synonyms' else attr for attr in tempHeader])
                outFile.write(fixedHeader + '\n')
                for outString in self.processNodeInfo():
                    outFile.write(outString + '\n')
            end = time.clock()
            duration = end - start
            print "\nIt took %s seconds to parse %s\n" % (duration, self.filePath)

        elif self.file.endswith('gene2go'):
            start = time.clock()
            print "Parsing %s\n" % self.filePath
            with open(self.outPath, 'w') as outFile:
                relnDict = self.processGeneGORelationshipInfo()
                # outHeader = self.outHeader[:-1]
                # outHeader.append(":Label")
                outHeader = self.fixHeader()
                outFile.write('|'.join(outHeader) + '\n')
                for relnTup, idSet in relnDict.iteritems():
                    fullIDList = ';'.join([medID for medID in idSet])
                    relnList = list(relnTup)
                    relnList.insert(-1, fullIDList)
                    outString = '|'.join(relnList)
                    outFile.write(outString + '\n')
            end = time.clock()
            duration = end - start
            print "\nIt took %s seconds to parse %s\n" % (duration, self.filePath)
            print len(relnDict), ' ENTREZ Gene to Gene Ontology relationships have been created.\n'

        elif self.file.endswith('gene_group'):
            start = time.clock()
            print "Parsing %s\n" % self.filePath
            relnDict = self.processGeneTaxRelationshipInfo()
            with open(self.outPath, 'w') as outFile:
                fixedHeader = self.fixHeader()
                # fixedHeader = self.fixHeader('relationship', 'Other_tax_id')
                outFile.write('|'.join(self.outHeader) + '\n')
                for relnTup, alternateIDs in relnDict.iteritems():
                    relnList = list(relnTup)
                    altGeneIDs = ';'.join(alternateIDs['Other_GeneID'])
                    altTaxIDs = ';'.join(alternateIDs['Other_tax_id'])
                    outFile.write('|'.join(relnList) + "|" + altGeneIDs + '|' + altTaxIDs + '\n')
            end = time.clock()
            duration = end - start
            print "\nIt took %s seconds to parse %s\n" % (duration, self.filePath)
            print len(relnDict), ' ENTREZ Gene to NCBI Taxonomy relationships have been created.\n'
        # elif self.file.endswith('mim2gene_medgen')

#  geneTaxRelnOutFile.write(":START_ID|alternate_tax_ids:string[]|source|alternate_gene_ids:string[]|:END_ID|:TYPE\n")



    def getPredicate(self, predicate):
        """ Hard codes text as string according to the disorder's phene mapping key. """
        predicateOptions = {'Component': "is_a",
                            'Function': "performs",
                            'Process': "part_of"}
        if predicate in predicateOptions:
            return predicateOptions[predicate]
        else:
            return ""

    def processGeneTaxRelationshipInfo(self):
        """
        Processes filteredRow which is yielded from self.parseTsvFIle().
        Returns defaultdict with (tax_id, relationship, geneID) as 
        composite key for aggregated pubmed IDs
        """
        relnDict = defaultdict(lambda: defaultdict(set))
        for filteredRow in self.parseTsvFile():
            zippedRow = OrderedDict(zip(self.outHeader, filteredRow))

            # filteredRow[self.outHeader.index('tax_id')] = 'NCBI_TAXONOMY:' + filteredRow[self.outHeader.index('tax_id')]
            # filteredRow[self.outHeader.index('GeneID')] = 'ENTREZ_GENE:' + filteredRow[self.outHeader.index('GeneID')]
            # filteredRow[self.outHeader.index('Other_tax_id')] = 'NCBI_TAXONOMY:' + filteredRow[self.outHeader.index('Other_tax_id')]
            # filteredRow[self.outHeader.index('Other_GeneID')] = 'ENTREZ_GENE:' + filteredRow[self.outHeader.index('Other_GeneID')]
            relnTup = (('NCBI_TAXONOMY:' + zippedRow['tax_id']), zippedRow['relationship'], ('ENTREZ_GENE:' + zippedRow['GeneID']))
            relnDict[relnTup]['Other_GeneID'].add(zippedRow['Other_GeneID'])
            relnDict[relnTup]['Other_tax_ID'].add(zippedRow['Other_tax_id'])
        return relnDict

    def processGeneGORelationshipInfo(self):
        relnDict = defaultdict(set)
        for filteredRow in self.parseTsvFile():
            zippedRow = OrderedDict(zip(self.outHeader, filteredRow))
            relnTuple = (('ENTREZ_GENE:' + zippedRow['GeneID']), zippedRow['GO_ID'], self.getPredicate(zippedRow['Category']))
            relnDict[relnTuple].update([medID for medID in zippedRow['PubMed'].split(';') if medID != '-'])
        return relnDict

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
