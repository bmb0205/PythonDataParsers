#!/usr/bin/python

from collections import defaultdict
from collections import OrderedDict
import locale
import time
from sourceclass import SourceClass


class NCBIEntrezGene():
    """
    Class for parsing All_Mammalia.gene_info, All_Plants.gene_info files
    Holds logic for processing NCBI Entrez Gene nodes in preparation for writing
    """
    print "\n~~~~~ Parsing NCBI Entrez Gene database ~~~~~\n"

    def __init__(self, file, source, outPath, filePath, outHeader,
                 inputAttributes, fileHeader, ignoredAttributes):
        self.parent = SourceClass(file, source, outPath, filePath, outHeader,
                                  inputAttributes, fileHeader, ignoredAttributes)

    def checkFile(self):

        if self.parent.file.endswith('gene_info'):
            self.parent.writeHeader()
            nodeSet = self.writeGeneNodes()
            self.parent.completeNodeSet.update(nodeSet)

        elif self.parent.file.endswith('gene2go'):
            self.parent.writeHeader()
            self.writeGeneToGOrelationships()

        elif self.parent.file.endswith('gene_group'):
            self.parent.writeHeader()
            self.writeGeneToTaxonomyRelationships()

        elif self.parent.file.endswith('mim2gene_medgen'):
            self.parent.writeHeader()
            self.writeGeneToMIMrelationships()

        elif self.parent.file.endswith('gene2pubmed'):
            self.parent.writeHeader()
            self.writeGeneToPubmedRelationships()

    def writeGeneNodes(self):
        """
        Processes row yielded from parseTsvFile() generator function
        Gathers synonyms based on user selection in .json
        Uses list comprehension to create and alter outString for node writing to out file
        """
        start = time.clock()
        nodeSet = set()
        print "Parsing %s\n" % self.parent.filePath
        with open(self.parent.outPath, 'a') as outFile:
            for filteredRow in self.parent.parseTsvFile():
                ignoredIndexList = [i for i, n in enumerate(self.parent.inputAttributes) if n in self.parent.ignoredAttributes]
                syndexList = [index for index, attr in enumerate(self.parent.inputAttributes) if attr.lower() in ['synonym', 'synonyms']]
                ignoredIndexList.extend(syndexList)
                tempList = [n for i, n in enumerate(filteredRow) if i not in ignoredIndexList and n != '-']
                synonyms = ";".join([filteredRow[i] for i in ignoredIndexList if filteredRow[i] != '-'])
                tempList.insert(self.parent.outHeader.index('Synonyms'), synonyms)
                tempList[0] = 'ENTREZ:' + tempList[0]
                nodeSet.add(tempList[0])  # before adding entrez gene label below
                outString = '|'.join(tempList)
                outFile.write(outString + '|' + self.parent.getFullSourceName() + '|Gene\n')
        end = time.clock()
        duration = end - start
        print "\n\tIt took %s seconds to parse this file.\n" % duration
        print '\t%s ENTREZ Gene nodes have been created.\n' % locale.format('%d', len(nodeSet), True)
        return nodeSet

    def writeGeneToMIMrelationships(self):
        """
        Processes filteredRow from parseTsvFile() generator located in base class.
        Ensures gene node exists before writing to outfile.
        Times execution and reports that and number of relationships created.
        """
        start = time.clock()
        print "Parsing %s\n" % self.parent.filePath
        relnCount = 0
        with open(self.parent.outPath, 'a') as outFile:
            for filteredRow in self.parent.parseTsvFile():
                zippedRow = OrderedDict(zip(self.parent.outHeader, filteredRow))
                zippedRow = self.parent.addSourceNames(zippedRow)
                if zippedRow['GeneID'] != '-' and zippedRow['GeneID'] in self.parent.completeNodeSet:
                    relnCount += 1
                    outString = ('|'.join(zippedRow.values()) + '|' + 'belongs_to' + '|' + self.parent.getFullSourceName())
                    outFile.write(outString + '\n')
        end = time.clock()
        duration = end - start
        print "\n\tIt took %s seconds to parse this file.\n" % duration
        print '\t%s Mendelian Inheritance in Man to NCBI Taxonomy relationships have been created.\n' % locale.format('%d', relnCount, True)

    def writeGeneToTaxonomyRelationships(self):
        """
        Processes filteredRow from parseTsvFile() generator located in base class.
        Ensures gene node exists before writing to outfile.
        Joins together altGeneIDs and altTaxIDs arrays using ';' for proper reading by neo4j-import.
        Times execution and reports that and number of relationships created.
        """
        start = time.clock()
        relnCount = 0
        print "Parsing %s\n" % self.parent.filePath
        with open(self.parent.outPath, 'a') as outFile:
            relnDict = self.processRelationshipInfo()
            for relnTup, alternateIDs in relnDict.iteritems():
                if relnTup[1] in self.parent.completeNodeSet:
                    relnCount += 1
                    relnList = list(relnTup)
                    altGeneIDs = ';'.join(alternateIDs['Other_GeneID'])
                    altTaxIDs = ';'.join(alternateIDs['Other_tax_id'])
                    outFile.write('|'.join(relnList) + "|" + altGeneIDs + '|' + altTaxIDs + '|' + self.parent.getFullSourceName() + '\n')
        end = time.clock()
        duration = end - start
        print "\n\tIt took %s seconds to parse this file.\n" % duration
        print '\t%s ENTREZ Gene to NCBI Taxonomy relationships have been created.\n' % locale.format('%d', relnCount, True)

    def writeGeneToGOrelationships(self):
        """
        Processes filteredRow from parseTsvFile() generator located in base class.
        Ensures gene node exists before writing to outfile.
        Joins together PubMed ID's rom idSet arrays using ';' for proper reading by neo4j-import.
        Times execution and reports that and number of relationships created.
        """
        start = time.clock()
        relnCount = 0
        print "Parsing %s\n" % self.parent.filePath
        with open(self.parent.outPath, 'a') as outFile:
            relnDict = self.processRelationshipInfo()
            for relnTup, idSet in relnDict.iteritems():
                if relnTup[0] in self.parent.completeNodeSet:
                    relnCount += 1
                    fullIDList = ';'.join([medID for medID in idSet])
                    relnList = list(relnTup)
                    relnList.insert(-1, fullIDList)
                    relnList.append(self.parent.getFullSourceName())
                    outString = '|'.join(relnList)
                    outFile.write(outString + '\n')
        end = time.clock()
        duration = end - start
        print "\n\tIt took %s seconds to parse this file.\n" % duration
        print '\t%s ENTREZ Gene to Gene Ontology relationships have been created.\n' % locale.format('%d', relnCount, True)

    def writeGeneToPubmedRelationships(self):
        """ """
        start = time.clock()
        relnCount = 0
        badCount = 0
        print "Parsing %s\n" % self.parent.filePath
        with open(self.parent.outPath, 'a') as outFile:
            for filteredRow in self.parent.parseTsvFile():
                geneID = "ENTREZ:" + filteredRow[0]
                if geneID in self.parent.completeNodeSet:
                    genePubmedReln = "%s|%s|associated_with|%s\n" % (geneID, filteredRow[1], self.parent.getFullSourceName())
                    outFile.write(genePubmedReln)
                    relnCount += 1
                else:
                    badCount += 1
                    #  make missing gene nodes here? why are they missing?
        end = time.clock()
        duration = end - start
        print badCount
        print "\n\tIt took %s seconds to parse this file.\n" % duration
        print '\t%s ENTREZ Gene to PubMed relationships have been created.\n' % locale.format('%d', relnCount, True)

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
        Processes filteredRow for gene2go and gene_group files, which is yielded from self.parseTsvFIle().
        Returns defaultdict with (tax_id, relationship, geneID) as composite key for aggregated pubmed IDs
        mim2gene_medgen relationships not included because they are written line by line and not aggregated.
        """
        if self.parent.file == 'gene2go':
            relnDict = defaultdict(set)
            for filteredRow in self.parent.parseTsvFile():
                zippedRow = OrderedDict(zip(self.parent.outHeader, filteredRow))
                zippedRow = self.parent.addSourceNames(zippedRow)
                relnTuple = (zippedRow['GeneID'], zippedRow['GO_ID'], self.getPredicate(zippedRow['Category']))
                relnDict[relnTuple].update([medID for medID in zippedRow['PubMed'].split(';') if medID != '-'])
            return relnDict

        elif self.parent.file == 'gene_group':
            relnDict = defaultdict(lambda: defaultdict(set))
            for filteredRow in self.parent.parseTsvFile():
                zippedRow = OrderedDict(zip(self.parent.outHeader, filteredRow))
                zippedRow = self.parent.addSourceNames(zippedRow)
                relnTup = (zippedRow['tax_id'], zippedRow['GeneID'], zippedRow['relationship'].replace(' ', '_'))
                relnDict[relnTup]['Other_GeneID'].add(zippedRow['Other_GeneID'])
                relnDict[relnTup]['Other_tax_ID'].add(zippedRow['Other_tax_id'])
            return relnDict
