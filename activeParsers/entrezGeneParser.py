#!/usr/bin/python

import sys
import os
import getopt
import collections
import locale
import time
import re
from collections import defaultdict
from entrezGeneClasses import EntrezNode
from entrezGeneClasses import GeneToTax
from entrezGeneClasses import GeneToGO
from entrezGeneClasses import GeneToMIM
# from entrezGeneClasses import MIMNode
# from entrezGeneClasses import MorbidMap
# from entrezGeneClasses import MIMToGene
# from entrezGeneClasses import MeSHNode

"""
##################################################################################################################
##########################################   NCBI Entrez Gene parser  #########################################################
##################################################################################################################

Parses NCBI Entrez Gene database files for graph database node and relationship creation.
See howToRun() method for instructions.
Infile(s): NCBI Entrez Gene files
Outfile(s): geneNodeOut.csv, geneTaxRelnout.csv, geneGORelnOut.csv, geneMIMRelnOut.csv

"""

def writeGeneNodes(geneFilePath, geneNodeOutFile, count):
	"""	writes NCBI entrez gene nodes to node outfile """
	geneSet = set()
	with open(geneFilePath, 'ru') as inFile:
		for line in inFile:
			if line.startswith("#"):
				continue
			count += 1
			columns = line.strip().split("\t")
			obj = EntrezNode(columns)
			if not obj.gene_id in geneSet:
				geneSet.add(obj.gene_id)
				synList = [obj.getSynonyms(), obj.getSymbolFromNom(), obj.getOtherDesignations(), obj.symbol]
				synList = filter(None, synList)
				synSet = set(synList)
				synString = ";".join(synSet)
				node = "%s|NCBI_Entrez_Gene|%s|%s|Gene\n" %(obj.gene_id, obj.preferred_term, synString)
				node = clean(node)
				geneNodeOutFile.write(node)
	print "\t\t\t\t\t\t    %s nodes have been created from this file\n" %locale.format('%d', count, True)
	return geneSet, count

def getPredicate(obj):
	predicate = ""
	if obj.predicate == "Component":
		predicate = "is_a"
	elif obj.predicate == "Function":
		predicate = "performs"
	elif obj.predicate == "Process":
		predicate = "part_of"
	return predicate

def geneGOReln(geneFilePath, geneGORelnOutFile, combined):  # NCBIEntrezGene/gene2go.... geneSet is number of unique nodes written (2,007,027)
	""" creates relationships for entrez gene to GO and writes to outfile """
	print "\t\t\t\t  Creating and writing NCBI Entrez Gene -> Gene Ontology (GO) relationships."
	with open(geneFilePath, 'ru') as inFile:
		geneGOMap = defaultdict(set)
		for line in inFile:
			if line.startswith("#"):
				continue
			columns = line.strip().split("\t")
			obj = GeneToGO(columns)
			if obj.gene_id in combined: # check if the node exists and was written
				predicate = getPredicate(obj)
				myKey = (obj.gene_id, predicate, obj.go_id)
				geneGOMap[myKey].add(obj.getPubmedID())
	writeGeneGOReln(geneGOMap, geneGORelnOutFile)
	return len(geneGOMap)

def writeGeneGOReln(geneGOMap, geneGORelnOutFile):
	count = 0
	for k, v in geneGOMap.iteritems():
		count += 1
		articles = filter(None, v)
		joinedArticles = ';'.join(articles)
		reln = "%s|NCBI_Entrez_Gene|%s|%s|%s\n" %(k[0], joinedArticles, k[2], k[1])
		geneGORelnOutFile.write(reln)
	print "\t\t\t%s NCBI Entrez Gene -> Gene Ontology (GO) relationships have been created from this file." %locale.format('%d', count, True)

def geneTaxReln(geneFilePath, geneTaxRelnOutFile, combined): # NCBIEntrezGene/gene_group
	""" creates relationships for entrez gene to NCBI taxonomy and writes to outfile """
	print "\t\t\t\t     Creating and writing NCBI Entrez Gene -> NCBI Taxonomy relationships."
	with open(geneFilePath, 'ru') as inFile:
		geneTaxMap = defaultdict(set)
		for line in inFile:
			if line.startswith("#") or "sibling" in line:
				continue
			columns = line.strip().split("\t")
			obj = GeneToTax(columns)
			if obj.gene_id in combined:
				myKey = (obj.tax_id, obj.predicate, obj.gene_id)
				geneTaxMap[myKey].add(obj.other_tax_id)
				geneTaxMap[myKey].add(obj.other_gene_id)
	writeGeneTaxReln(geneTaxMap, geneTaxRelnOutFile)
	return len(geneTaxMap)

def writeGeneTaxReln(geneTaxMap, geneTaxRelnOutFile):
	count = 0
	for k, v in geneTaxMap.iteritems():
		count += 1
		altGeneList = list()
		altTaxList = list()
		source = "NCBI_Entrez_Gene"
		for alt_id in v:
			if "ENTREZ" in alt_id:
				altGeneList.append(alt_id)
			elif "TAXONOMY" in alt_id:
				altTaxList.append(alt_id)
		altGeneString = ';'.join(altGeneList)
		altTaxString = ';'.join(altTaxList)
		reln = "%s|%s|%s|%s|%s|%s\n" %(k[0], altTaxString, source, altGeneString, k[2], k[1])
		geneTaxRelnOutFile.write(reln)
	print "\t\t\t\t%s NCBI Entrez Gene -> NCBI Taxonomy relationships have been created from this file." %locale.format('%d', count, True)

def geneMIMReln(geneFilePath, geneMIMRelnOutFile, combined): # NCBIEntrezGene/mim2gene_medgen.txt
	""" creates relationships for entrez gene to MIM and writes to outfile """
	print "\t\t\t\t\t     Creating and writing NCBI Entrez Gene -> MIM relationships"
	relnSet = set()
	duplicateRelns = geneFilePath.rsplit("/", 2)[0] + "/csv_out/duplicateGeneMIMReln.csv"
	with open(geneFilePath, 'ru') as inFile, open(duplicateRelns, 'w') as duplicateRelnOutFile:
		duplicateRelnOutFile.write("# relationships that contain both gene and phenotype duplicates")
		for line in inFile:
			if line.startswith("#"):
				continue
			columns = line.strip().split("\t")
			obj = GeneToMIM(columns)
			if obj.gene_id in combined:
				myKey = (obj.gene_id, "NCBI_Entrez_Gene", "belongs_to", obj.MIM_id)
				if myKey in relnSet:
					duplicateRelnOutFile.write("|".join(myKey) + "\n")
				relnSet.add(myKey)
	writeGeneMIMReln(relnSet, geneMIMRelnOutFile)
	return len(relnSet)

def writeGeneMIMReln(relnSet, geneMIMRelnOutFile):
	count = 0
	for reln in relnSet:
		count += 1
		joined = "|".join(reln)
		joined = joined + "\n"
		cleaned = clean(joined)
		geneMIMRelnOutFile.write(cleaned)
	print "\t\t\t\t%s NCBI Entrez Gene -> MIM relationships have been created from this file." %locale.format('%d', count, True)


##################################################################################################################
##########################################   General   #########################################################
##################################################################################################################

def createOutDirectory(topDir):
	""" Creates path for out directory and outfiles """
	outPath = (str(topDir) + "csv_out/")
	if not os.path.exists(outPath):
		os.makedirs(outPath)
		print "\n\n\t\t\tOutfile directory path not found...\n\t\tOne created at %s\n" %outPath
	return outPath

def clean(string):
	""" cleans lines of any characters that may affect neo4j database creation or import """
	cleaned = string.replace(";", ",")
	return cleaned

def howToRun():
	""" 
	Instructs users how to use script.
	opts/args: -h, help
	"""
	print "\n\t\t * Run as: python /path/to/this/script.py -p /path/to/top/directory"
	print "\n\t\t * Example top directory: /Users/username/KnowledgeBasedDiscovery/"
	print "\n\t\t * Top directory structure: \n\t\t\t * /Users/username/KnowledgeBasedDiscovery/<subdir>/<files>"
	print "\t\t\t\t * <subdir> : NCBIEntrezGene/"
	print "\t\t\t\t * <subfiles> : *"
	sys.exit(2) 


def main(argv):
	"""
	If run as main script, function executes.
	"""
	topDir = ""
	try:
		opts, args = getopt.getopt(argv,"hp:",["help","dirPath="])
		if len(argv) == 0:
			howToRun()
	except getopt.GetoptError:
		howToRun()
	for opt, arg in opts:
		if opt == "-h":
			howToRun()
		elif opt in ("-p", "--dirPath"):
			if not arg.endswith("/"):
				arg = arg + "/"
			startTime = time.clock()
			topDir = arg
			locale.setlocale(locale.LC_ALL, "")
			outPath = createOutDirectory(topDir)

			""" ENTREZ Gene """
			geneNodeOutFile = open((outPath + 'geneNodeOut.csv'), 'w')
			geneTaxRelnOutFile = open((outPath + 'geneTaxRelnOut.csv'), 'w')
			geneGORelnOutFile = open((outPath + 'geneGORelnOut.csv'), 'w')
			geneMIMRelnOutFile = open((outPath + 'geneMIMRelnOut.csv'), 'w')

			geneNodeOutFile.write("source_id:ID|source|preferred_term|synonyms:string[]|:LABEL\n")
			geneTaxRelnOutFile.write(":START_ID|alternate_tax_ids:string[]|source|alternate_gene_ids:string[]|:END_ID|:TYPE\n")
			geneGORelnOutFile.write(":START_ID|source|pubmed_articles:string[]|:END_ID|:TYPE\n")
			geneMIMRelnOutFile.write(":START_ID|source|:END_ID|:TYPE\n")

			for root, dirs, files in os.walk(topDir):
				
				""" NCBI ENTREZ GENE """
				if root.endswith("NCBIEntrezGene"):
					count = 0
					print "\n\n\n\t\t\t================================ PARSING NCBI Entrez Gene Database ==================================="
					print "\n\t\t\t\t\t\t\t\tProcessing files in:\n"
					nodeCountList = list()
					nodeList = list()
					for geneFile in files:
						geneFilePath = os.path.join(root, geneFile)
						if geneFilePath.endswith(".gene_info"):
							print "\t\t\t\t\t\t%s" %geneFilePath
							geneSet, geneNodeCount = writeGeneNodes(geneFilePath, geneNodeOutFile, count)
							nodeList.append(geneSet)
							nodeCountList.append(len(geneSet))
						if geneFilePath.endswith("gene2go"):
							combined = nodeList[0].union(nodeList[1])
							print "\n\t\t\t\t\t\t%s" %geneFilePath
							geneGORelnCount = geneGOReln(geneFilePath, geneGORelnOutFile, combined)
						if geneFilePath.endswith("gene_group"):
							print "\n\t\t\t\t\t\t%s" %geneFilePath
							geneTaxRelnCount = geneTaxReln(geneFilePath, geneTaxRelnOutFile, combined)
						if geneFilePath.endswith("medgen"):
							print "\n\t\t\t\t\t%s" %geneFilePath
							geneMIMRelnCount = geneMIMReln(geneFilePath, geneMIMRelnOutFile, combined)
					endTime = time.clock()
					duration = endTime - startTime
					print "\n\t\t\t\t\t   %s total NCBI Entrez Gene nodes have been created..." %locale.format('%d', (nodeCountList[0] + nodeCountList[1]), True)
					print "\n\t\t\t\t\t   %s total NCBI Entrez Gene relationships have been created." %locale.format('%d', (geneGORelnCount + geneTaxRelnCount + geneMIMRelnCount), True)
					print "\n\t\t\t\t\tIt took %s seconds to create all NCBI Entrez nodes and relationships\n" %duration


if __name__ == "__main__":
	main(sys.argv[1:])

