#!/usr/bin/python

import sys
import os
import getopt
import locale
import time
from collections import defaultdict
from taxonomyClasses import TaxNamesParser
from taxonomyClasses import TaxNodesParser
from taxonomyClasses import TaxCitationsParser


"""
##################################################################################################################
##########################################   NCBI Taxonomy Parser   #########################################################
##################################################################################################################

Parses NCBI Taxonomy database files for graph database node and relationship creation.
See howToRun() method for instructions.
Infile(s): NCBI Taxonomy (*.dmp) files
Outfile(s): taxNodeOut.csv, taxRelnOut.csv

"""

def parseNodes(taxFilePath, taxMap):
	""" parses nodes.dmp and adds 'parent_tax_id' and 'rank' properties to taxMap """
	with open(taxFilePath, 'ru') as stream:
		count = 0
		for line in stream:
			count += 1
			columns = line.split("|")
			nodeObj = TaxNodesParser(columns)
			taxMap[nodeObj.node] = {"parent_tax_id" : nodeObj.parent, "rank" : nodeObj.rank}
	return taxMap

def parseNames(namesFilePath, taxMap):
	""" parses names.dmp and adds 'term', 'synonyms' and 'preferred_term' properties to taxMap """
	with open(namesFilePath, 'ru') as stream:
		synonymDict = dict()
		for line in stream:
			columns = line.split("|")
			nameObj = TaxNamesParser(columns)
			node = nameObj.node
			term = nameObj.term
			preferred_term = nameObj.getPreferred()
			if not nameObj.node in synonymDict:
				synonymDict[node] = set()
				synonymDict[node].add(term)
				synonymDict[node].add(preferred_term)
			else:
				synonymDict[node].add(term)
				synonymDict[node].add(preferred_term)
			taxMap[node]["preferred_term"] = preferred_term
			taxMap[node]["term"] = term
		for node, synonyms in synonymDict.iteritems():
			taxMap[node]["synonyms"] = synonyms
	return taxMap

def parseCitations(citationsFilePath, taxMap):
	""" Gets medline IDs for each tax_id and adds medline_id item to taxMap """
	with open(citationsFilePath, 'ru') as stream:
		for line in stream:
			columns = line.strip().split("|")
			citationObj = TaxCitationsParser(columns)
			if citationObj.medline_id != "0":
				for node in citationObj.nodeList:
					if node != "":
						nodeID = ("NCBI_TAXONOMY:" + node)
						taxMap[nodeID]["medline_id"] = citationObj.medline_id
	return taxMap

def writeTaxData(taxMap, taxNodeOutFile, taxRelnOutFile):
	"""
	Writes taxonomy nodes and relationships to outfiles.
	Outfiles: topDir/csv_out/taxNodeOutFile.csv, topDir/csv_out/taxRelnOutFile.csv
	"""
	count = 0
	print "\n\t\t\t\t\t\t  Creating and writing NCBI Taxonomy nodes and relationships..."
	for tax_id, properties in taxMap.iteritems():
		count += 1
		if not "medline_id" in properties:
			properties['medline_id'] = ""
		node = '%s|NCBI_Taxonomy|%s|%s|%s|%s|%s|Plant\n' %(tax_id, properties["term"], properties["preferred_term"], properties["rank"], ";".join(properties["synonyms"]), properties["medline_id"])
		node = clean(node)
		taxNodeOutFile.write(node)
		reln = '%s|NCBI_Taxonomy|%s|is_a\n' %(tax_id, properties["parent_tax_id"])
		reln = clean(reln)
		taxRelnOutFile.write(reln)
	print "\n\t\t\t\t\t\t\t%s NCBI Taxonomy nodes have been created...\n" %locale.format('%d', count, True)
	print "\t\t\t\t\t\t   %s NCBI Taxonomy relationships have been created...\n" %locale.format('%d', count, True)


##################################################################################################################
##########################################   General   #########################################################
##################################################################################################################


def createOutDirectory(topDir):
	""" creates path for out directory and outfiles """
	outPath = (str(topDir) + "csv_out/")
	if not os.path.exists(outPath):
		os.makedirs(outPath)
		print "\n\n\t\t\tOutfile directory path not found...\n\t\tOne created at %s\n" %outPath
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
			getHelp()
	except getopt.GetoptError:
		getHelp()
	for opt, arg in opts:
		if opt == '-h':
			getHelp()
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
			print "\n\n\n\t\t\t\t=====================================  PARSING NCBI Taxonomy ====================================="
			print "\n\t\t\t\t\t\t\t\t\tProcessing files in:\n\n\t\t\t\t\t\t    %s\n" %taxRoot
			print "\n\t\t\t\t\t\t\t\t\t Files processed: "

			taxMap = dict()
			for root, dirs, files in os.walk(topDir):
				if root.endswith("NCBITaxonomy"):
					for taxFile in files:
						taxFilePath = os.path.join(root, taxFile)
						if taxFilePath.endswith("nodes.dmp"):

							print "\n\t\t\t\t\t\t %s " %taxFilePath
						 	taxMap = parseNodes(taxFilePath, taxMap)

						 	namesFilePath = os.path.join(root, "names.dmp")
						 	print "\n\t\t\t\t\t\t %s " %namesFilePath
						 	taxMap.update(parseNames(namesFilePath, taxMap))

						 	citationsFilePath = os.path.join(root, "citations.dmp")
						 	print "\n\t\t\t\t\t\t %s\n " %citationsFilePath
						 	taxMap.update(parseCitations(citationsFilePath, taxMap))

					writeTaxData(taxMap, taxNodeOutFile, taxRelnOutFile)

			endTime = time.clock()
			duration = endTime - startTime
			print "\t\t\t\t\t   It took %s seconds to create all NCBI Taxonomy nodes and relationships\n" %duration

if __name__ == "__main__":
	main(sys.argv[1:])