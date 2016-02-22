#!/usr/bin/python

import sys
import os
import getopt
import collections
import locale
import time
import re
from collections import defaultdict
from operator import itemgetter
from omimClasses import MIMNode
from omimClasses import MIMToGene
from omimClasses import DisorderNode

"""
Main file parser used to parse and extract data from OMIM database.
Parsed information is written to pipe delimited .csv outfiles in a directory created by the script.
See howToRun() method below for help running script.
Written by: Brandon Burciaga
"""

##################################################################################################################
#########################################   MIM   ###########################################################
##################################################################################################################

# 15705 unique gene nodes total
def writeMIMgeneNodes(MIMFilePath, mimGeneNodeOutFile): # MIM/geneMap2.txt
	"""	writes MIM gene nodes to mimGeneNodeOutFile, writes MIM relationships to mimRelnOutFile """
	relnSet = set()
	geneNodeCount = 0
	geneSet = set()
	relnMap = defaultdict(set)
	with open(MIMFilePath, 'ru') as inFile: #15,755 gene nodes
		for line in inFile:
			columns = line.replace("''", "").replace("'", "prime").split("|")
			geneObj = MIMNode(columns)
			mimGeneNode = "%s|OMIM|%s|%s|%s|Gene\n" %(geneObj.gene_id, geneObj.name, geneObj.cytogenetic_location, geneObj.getGeneSymbols())
			mimGeneNodeOutFile.write(mimGeneNode)
			geneNodeCount += 1
			geneSet.add(geneObj.gene_id)
			if not geneObj.disorder_info == "": # 4786 genes associated with disorders
				for reln in geneObj.getDisorderInfo():
					if not reln[0] == reln[2]:
						relnMap['genes'].add(reln)
						relnSet.add(reln)
					else:
						fixedReln = (reln[0], reln[1], (reln[2] + 'p'))
						relnSet.add(fixedReln)
						relnMap['genes'].add(fixedReln)
			else:
				continue
	print "\n\t\t\t\t\t\t\t%s OMIM gene nodes have been created..." %locale.format('%d', geneNodeCount, True)
	return relnSet, relnMap, geneNodeCount, geneSet



# 5870 disorder nodes total
def parseMIMDisorderNodes(MIMFilePath, relnSet, relnMap, geneSet):
	""" Constructs and fills map of disorder information for each node, then iterates and writes to mimDisorderNodeOutFile """
	aCount = 0
	disorderMap = defaultdict(set)
	with open(MIMFilePath, 'ru') as inFile:
		for line in inFile:
			columns = line.replace("''", "").replace("'", "prime").split("|")
			disObj = DisorderNode(columns)

			# 5 disorder nodes that should not have ID in text since it is same as gene ID
			# ['MIM:615538', 'MIM:602782', 'MIM:615162', 'MIM:615022', 'MIM:185900']
			# example: Chromosome 22q13 duplication syndrome, 615538 (4)|DUP22q13, C22DUPq13|615538|22q13
			# fix: make disorder ID the geneID + 'p'
			if disObj.disorderID == disObj.geneMIM:
				disObj.setDisorderID()
				fixedTup = (disObj.disorderID, disObj.pheneKey, disObj.geneMIM)
				disorderMap[disObj.disorderID].add(disObj)
				relnMap['disorders'].add(fixedTup)
			
			# 6978
			else:
				if disObj.disorderID in geneSet:
					disObj.setDisorderID()
				disorderMap[disObj.disorderID].add(disObj)
				relnTup = (disObj.disorderID, disObj.pheneKey, disObj.geneMIM)
				relnMap['disorders'].add(relnTup)
	return relnSet, relnMap, disorderMap

#5870 disorder nodes written total
def writeMIMDisorderNodes(disorderMap, mimDisorderNodeOutFile):
	""" Iterates disorderMap and writes disorder nodes depending on varying conditionals """
	disorderNodeCount = 0
	disorderTextMap = defaultdict(set)
	for k, v in disorderMap.iteritems():
		myList = list()
		synonymSet = set()

		# 504 nodes written with at least one duplicate...take best pheneKey and text, other text are synonyms
		if len(v) > 1:
			for obj in v:
				textPhene = (obj.pheneKey, obj.text.rstrip(','))
				if not textPhene in myList:
					myList.append(textPhene)
			# sort list, separate primary (pheneKey, text) from other tuples which become synonyms
			sortedList = sorted(myList, key = itemgetter(0))
			rawText = sortedList[-1][1]
			text = clean(rawText)
			textSymbols = rawText[:2]
			disorderTextMap[k].add(textSymbols)
			pheneKey = getPheneKey(sortedList[-1][0])
			other = sortedList[:-1]
			for item in other:
				synonymSet.add(clean(item[1]))
			disorderNodeCount += 1
			mimDisorderNode = "%s|OMIM|%s|%s|Phenotype\n" %(k, text, "; ".join(synonymSet))
			mimDisorderNodeOutFile.write(mimDisorderNode)

		# 5366 nodes written with no duplicates
		else: 
			disorderNodeCount += 1
			obj = v.pop()
			text = clean(obj.text)
			textSymbols = obj.text[:2]
			disorderTextMap[k].add(textSymbols)
			mimDisorderNode = "%s|OMIM|%s|%s|Phenotype\n" %(k, text, "")
			mimDisorderNodeOutFile.write(mimDisorderNode)
	print "\n\t\t\t\t\t\t\t%s OMIM disorder nodes have been created..." %locale.format('%d', disorderNodeCount, True)
	return disorderTextMap, disorderNodeCount


def getPheneKey(pheneKey):
	""" Hard codes text as string according to the disorder's phene mapping key """
	if pheneKey == "1":
		return "Disorder placed by association. Underlying defect unknown."
	elif pheneKey == "2":
		return "Disorder placed by linkage. No mutation found."
	elif pheneKey == "3":
		return "Disorder has known molecular basis. Mutation found."
	else:
		return "Contiguous gene deletion or duplication syndrome. Multiple genes are deleted or duplicated."

def getStatus(text):
	""" Hard codes and returns text as string according to OMIM symbols """
	if text == "{?":
		return "Mutation contributing to susceptibility to multifactorial disorders or infection. Unconfirmed or possibly spurrious mapping."
	elif text.startswith("{"):
		return "Mutation contributing to susceptibility to multifactorial disorders or infection."
	elif text.startswith("?"):
		return "Unconfirmed or possibly spurrious mapping."
	elif text.startswith("["):
		return "Non-disease. Genetic variation leading to abnormal lab test values."
	else:
		return ""

def writeMIMRelns(relnSet, relnMap, mimGeneRelnOutFile, mimDisorderRelnOutFile, disorderTextMap):
	""" Iterates through 'gene' and 'disorder' relationship sets within relnMap and writes relationships to outfiles """
	relnCount = 0
	for reln in relnMap['genes']:
		status = ''
		relnCount += 1
		statusSet = disorderTextMap[reln[-1]]
		status = getStatus("".join(statusSet))
		pheneKey = getPheneKey(reln[1])
		relnString = "%s|OMIM|%s|%s|%s|causes_phenotype\n" %(reln[0], reln[2], status, pheneKey)
		mimGeneRelnOutFile.write(relnString)
	for reln in relnMap['disorders']:
		relnCount += 1
		statusSet = disorderTextMap[reln[0]]
		status = getStatus("".join(statusSet))
		pheneKey = getPheneKey(reln[1])
		relnString = "%s|OMIM|%s|%s|%s|caused_by_gene\n" %(reln[0], reln[2], status, pheneKey)
		mimDisorderRelnOutFile.write(relnString)
	print "\n\t\t\t\t\t\t\t%s OMIM relationships have been created...\n" %locale.format('%d', relnCount, True)

def MIMGeneReln(MIMFilePath, mimEntrezRelnOutFile):
	""" Adds MIM --> Entrez gene relationships to unique set, writes to mimGeneRelnOutFile """
	relnSet2 = set()
	with open(MIMFilePath, 'ru') as inFile:
		for line in inFile:
			if line.startswith("#"):
				continue
			columns = line.strip().split('\t')
			if len(columns) >= 3:
				obj = MIMToGene(columns)
				myKey = ""
				if obj.type == "phenotype":
					myKey = (obj.gene_id, "NCBI_Entrez_Gene", (obj.MIM_id + "p"), "belongs_to")
				elif obj.type == "gene":
					myKey = (obj.gene_id, "NCBI_Entrez_Gene", obj.MIM_id, "belongs_to")
				relnSet2.add(myKey)
	relnCount = 0
	for reln in relnSet2:
		relnCount += 1
		mimEntrezRelnOutFile.write("|".join(reln) + "\n")
	print "\n\t\t\t\t\t  %s OMIM --> NCBI Entrez Gene relationships have been created..." %locale.format('%d', relnCount, True)

#################################################################################################################
#########################################   GENERAL   ###########################################################
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
	cleaned = string.rstrip("}").rstrip(')').rstrip(']').lstrip('{?').lstrip('{').lstrip('?').lstrip('[')
	return cleaned

def howToRun():
	""" 
	Instructs users how to use script.
	opts/args: -h, help
	"""
	print "\n\t\t * Run as: python /path/to/this/script.py -p /path/to/top/directory"
	print "\n\t\t * Example top directory: /Users/username/KnowledgeBasedDiscovery/"
	print "\n\t\t * Top directory structure: \n\t\t\t * /Users/username/KnowledgeBasedDiscovery/<subdir>/<files>"
	print "\t\t\t\t * <subdir> : OMIM/"
	print "\t\t\t\t * <subfiles> : *\n"
	sys.exit() 

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

			""" OMIM """
			mimGeneNodeOutFile = open((outPath + 'mimGeneNodeOut.csv'), 'w')
			mimDisorderNodeOutFile = open((outPath + 'mimDisorderNodeOut.csv'), 'w')
			mimGeneRelnOutFile = open((outPath + 'mimGeneRelnOut.csv'), 'w')
			mimDisorderRelnOutFile = open((outPath + 'mimDisorderRelnOut.csv'), 'w')
			mimEntrezRelnOutFile = open((outPath + 'mimEntrezRelnOut.csv'), 'w')

			mimGeneNodeOutFile.write("Source_ID:ID|Source|Name|Cytogenetic_Location|Gene_Symbol:string[]|:LABEL\n")
			mimDisorderNodeOutFile.write("Source_ID:ID|Source|Name|Synonyms:string[]|:LABEL\n")
			mimGeneRelnOutFile.write(":START_ID|Source|:END_ID|Status|Phenotype_Mapping_Method|:TYPE\n")
			mimDisorderRelnOutFile.write(":START_ID|Source|:END_ID|Status|Phenotype_Mapping_Method|:TYPE\n")
			mimEntrezRelnOutFile.write(":START_ID|Source|:END_ID|:TYPE")

			for root, dirs, files in os.walk(topDir):
				
				""" OMIM """
				if root.endswith("OMIM"):
					print "\n\n\n\t\t\t================ PARSING ONLINE MENDELIAN INHERITANCE IN MAN (OMIM) DATABASE ======================"
					print "\n\t\t\t\t\t\t\t\tProcessing files in:"
					for MIMFile in files:
						MIMFilePath =  os.path.join(root, MIMFile)
						if MIMFilePath.endswith("geneMap2.txt"):
							print "\n\t\t\t\t\t\t\t%s" %MIMFilePath
							relnSet, relnMap, geneNodeCount, geneSet = writeMIMgeneNodes(MIMFilePath, mimGeneNodeOutFile)
						if MIMFilePath.endswith("morbidmap"):
							print "\n\t\t\t\t\t\t\t%s" %MIMFilePath
							relnSet, relnMap, disorderMap = parseMIMDisorderNodes(MIMFilePath, relnSet, relnMap, geneSet)
							disorderTextMap, disorderNodeCount = writeMIMDisorderNodes(disorderMap, mimDisorderNodeOutFile)
							writeMIMRelns(relnSet, relnMap, mimGeneRelnOutFile, mimDisorderRelnOutFile, disorderTextMap)
						if MIMFilePath.endswith("mim2gene.txt"):
							print "\n\t\t\t\t\t\t\t%s" %MIMFilePath							
							MIMGeneReln(MIMFilePath, mimEntrezRelnOutFile)
			endTime = time.clock()
			duration = endTime - startTime
			print "\t\t\t\t\t\t\t%s total OMIM nodes have been created..." %locale.format('%d', (disorderNodeCount + geneNodeCount), True)
			print "\n\t\t\t\t\tIt took %s seconds to create all OMIM nodes and relationships\n" %duration

if __name__ == "__main__":
	main(sys.argv[1:])