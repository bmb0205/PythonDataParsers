#!/usr/bin/python

import sys
import os
import getopt
import locale
import time
from collections import defaultdict
# from taxonomyClasses import TaxNamesParser


"""
##################################################################################################################
##########################################   NCBI Taxonomy Parser   #########################################################
##################################################################################################################

Written by: Brandon Burciaga

* Parses NCBI Taxonomy database files for neo4j graph database node and relationship creation.
* Outfiles are .csv (pipe delimited) and generated with first line header demonstrating
	the format of the rest of the file (in columns)
* See howToRun() method for instructions using this script.
* Infile(s) [NCBI Taxonomy files in .dmp format, 2015 versions used]:
	* nodes.dmp, ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/
	* names.dmp, ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/
	* citations.dmp, ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/
* Outfile(s): taxNodeOut.csv, taxRelnOut.csv
* Imports: taxonomyClasses.py
"""

class TaxNamesParser(object):
    """ creates object for names.dmp """
    def __init__(self, columns):
        self.columns = columns
        self.node = "NCBI_TAXONOMY:" + columns[0].strip()
        self.term = columns[1].strip()
        self.preferredTerm = columns[2].strip()

    def getPreferred(self):
        """ gets preferred term. If none available, uses name as preferred term """
        if self.preferredTerm == "":
            return self.term
        return self.preferredTerm

    def getSynonyms(self):
        """ adds synonyms to set, return set """
        synonymSet = set()
        synonymSet.add(self.term)
        if not self.preferredTerm == "":
            synonymSet.add(self.preferredTerm)
        return synonymSet


def parseNodes(taxFilePath):
	""" parses nodes.dmp and adds 'parentTaxID' and 'rank' properties to taxMap """
	taxMap = defaultdict(dict)
	with open(taxFilePath, 'rU') as stream:
		for line in stream:
			columns = line.split("\t|\t")
			node = "NCBI_TAXONOMY:" + columns[0].strip()
			parent = "NCBI_TAXONOMY:" + columns[1].strip()
			rank = columns[2].strip()
			# print node
        	taxMap[node]['parentTaxID'] = parent
        	taxMap[node]['rank'] = rank
	print taxMap
	return taxMap

def parseNames(namesFilePath, taxMap):
	""" parses names.dmp and adds 'term', 'synonyms' and 'preferredTerm' properties to taxMap """
	with open(namesFilePath, 'rU') as stream:
		synonymDict = dict()
		for line in stream:
			columns = line.split("|")
			nameObj = TaxNamesParser(columns)
			print vars(nameObj)
			if not nameObj.node in synonymDict:
				synonymDict[nameObj.node] = set()
				synonymDict[nameObj.node].add(nameObj.term)
				synonymDict[nameObj.node].add(nameObj.getPreferred())
			else:
				synonymDict[nameObj.node].add(nameObj.term)
				synonymDict[nameObj.node].add(nameObj.getPreferred())
			taxMap[nameObj.node]["preferredTerm"] = nameObj.getPreferred()
			taxMap[nameObj.node]["term"] = nameObj.term
		for node, synonyms in synonymDict.iteritems():
			taxMap[node]["synonyms"] = synonyms
	return taxMap

def parseCitations(citationsFilePath, taxMap):
	""" Gets medline IDs for each tax_id and adds medlineID item to taxMap """
	with open(citationsFilePath, 'ru') as stream:
		for line in stream:
			columns = line.strip().split("|")
			medlineID = columns[3].strip()
			nodeList = columns[-2].strip().split(" ")
			if not medlineID == "0":
				for node in nodeList:
					if node:
						nodeID = ("NCBI_TAXONOMY:" + node)
						taxMap[nodeID]["medlineID"] = medlineID
	return taxMap

def writeTaxData(taxMap, taxNodeOutFile, taxRelnOutFile):
	"""
	Writes taxonomy nodes and relationships to outfiles.
	Outfiles: topDir/csv_out/taxNodeOutFile.csv, topDir/csv_out/taxRelnOutFile.csv
	"""
	count = 0
	print "\nCreating and writing NCBI Taxonomy nodes and relationships..."
	for tax_id, properties in taxMap.iteritems():
		count += 1
		if not "medlineID" in properties:
			properties['medlineID'] = ""
		node = '%s|NCBI_Taxonomy|%s|%s|%s|%s|%s|Plant\n' %(tax_id, properties["term"], properties["preferredTerm"], properties["rank"], ";".join(properties["synonyms"]), properties["medlineID"])
		node = clean(node)
		taxNodeOutFile.write(node)
		reln = '%s|NCBI_Taxonomy|%s|is_a\n' %(tax_id, properties["parentTaxID"])
		reln = clean(reln)
		taxRelnOutFile.write(reln)
	print "\n%s NCBI Taxonomy nodes have been created...\n" %locale.format('%d', count, True)
	print "%s NCBI Taxonomy relationships have been created...\n" %locale.format('%d', count, True)


##################################################################################################################
##########################################   General   #########################################################
##################################################################################################################


def createOutDirectory(topDir):
	""" creates path for out directory and outfiles """
	outPath = (str(topDir) + "csv_out/")
	if not os.path.exists(outPath):
		os.makedirs(outPath)
		print "\n\nOutfile directory path not found...\n\tOne created at %s\n" %outPath
	return outPath

def clean(string):
	"""	cleans lines of any characters that may affect neo4j database creation or import """
	cleaned = string.replace("'", "").replace('"', '')
	return cleaned

def howToRun():
	""" 
	Instructs users how to use script.
	opts/args: -h, help
	"""
	print "\n\t\t * Run as: python /path/to/this/script.py -p /path/to/top/directory"
	print "\n\t\t * Example top directory: /Users/username/KnowledgeBasedDiscovery/"
	print "\n\t\t * Top directory structure: \n\t\t\t * /Users/username/KnowledgeBasedDiscovery/<subdir>/<files>"
	print "\t\t\t\t * <subdir> : NCBITaxonomy/"
	print "\t\t\t\t * <subfiles> : *.dmp\n"
	sys.exit(2) 

def main(argv):
	"""
	If run as main script, function executes.
	"""
	topDir = ''
	try:
		opts, args = getopt.getopt(argv,"hp:",["help","dirPath="])
		if len(argv) == 0:
			howToRun()
	except getopt.GetoptError:
		howToRun()
	for opt, arg in opts:
		if opt == '-h':
			howToRun()
		elif opt in ("-p", "--dirPath"):
			if not arg.endswith("/"):
				arg = arg + "/"
			startTime = time.clock()
			topDir = arg
			locale.setlocale(locale.LC_ALL, "")
			outPath = createOutDirectory(topDir)

			taxNodeOutFile = open((outPath + 'taxNodeOut.csv'), 'w')
			taxRelnOutFile = open((outPath + 'taxRelnOut.csv'), 'w')
			taxNodeOutFile.write("Source_ID:ID|Source|Term|Preferred_Term|Rank|Synonyms:string[]|Medline_ID|:LABEL\n")
			taxRelnOutFile.write(":START_ID|Source|:END_ID|:TYPE\n")

			taxRoot = topDir + "NCBITaxonomy/"
			print "\n\n=====================================  PARSING NCBI Taxonomy ====================================="
			print "\nProcessing files in:\n\n%s\n" %taxRoot
			print "\nFiles processed: "

			for root, dirs, files in os.walk(topDir):
				if root.endswith("NCBITaxonomy"):
					for taxFile in files:
						taxFilePath = os.path.join(root, taxFile)
						if taxFilePath.endswith("nodes.dmp"):
							print 'ugh'
							print "\n%s " %taxFilePath
						 	taxMap = parseNodes(taxFilePath)

						 	for k, v in taxMap.iteritems():
						 		print k, v
			# 			 	namesFilePath = os.path.join(root, "names.dmp")
			# 			 	print "\n%s " %namesFilePath
			# 			 	taxMap.update(parseNames(namesFilePath, taxMap))

			# 			 	citationsFilePath = os.path.join(root, "citations.dmp")
			# 			 	print "\n%s\n " %citationsFilePath
			# 			 	taxMap.update(parseCitations(citationsFilePath, taxMap))

			# 		writeTaxData(taxMap, taxNodeOutFile, taxRelnOutFile)

			# endTime = time.clock()
			# duration = endTime - startTime
			# print "It took %s seconds to create all NCBI Taxonomy nodes and relationships\n" %duration

if __name__ == "__main__":
	main(sys.argv[1:])