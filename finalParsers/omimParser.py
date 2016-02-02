#!/usr/bin/python

import sys
import os
import getopt
import collections
import locale
import time
import re
from collections import defaultdict
from omimClasses import MIMNode
from omimClasses import MIMToGene


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
def writeMIMgeneNodes(MIMFilePath, mimGeneNodeOutFile, mimRelnOutFile): # MIM/geneMap2.txt
	"""	writes MIM gene nodes to mimGeneNodeOutFile, writes MIM relationships to mimRelnOutFile """
	nodeCount = 0
	relnCount = 0
	with open(MIMFilePath, 'ru') as inFile:
		uniqueSet = set()
		for line in inFile:
			nodeCount += 1
			columns = line.replace("''", "").replace("'", "prime").split("|")
			obj = MIMNode(columns)
			mimGeneNode = "%s|OMIM|%s|%s|%s|Gene\n" %(obj.gene_id, obj.getGeneSymbols(), obj.cytogenetic_location, obj.name)
			mimGeneNodeOutFile.write(mimGeneNode) 
			if not obj.disorder_info == "": # 4786 genes associated with disorders
				relnSet = obj.getDisorderInfo()
				for reln in relnSet:
					if not reln[1] in uniqueSet:
						relnCount += 1
						uniqueSet.add(reln[1])
						status = getStatus(reln[0])
						mimReln = "%s|OMIM|%s|%s|causes_phenotype\n" %(obj.gene_id, reln[1], status)
						mimRelnOutFile.write(mimReln)
	print "\n\t\t\t\t\t\t\t%s OMIM gene nodes have been created..." %locale.format('%d', nodeCount, True)
	print "\n\t\t\t\t\t\t\t%s OMIM relationships have been created...\n" %locale.format('%d', relnCount, True)


def getStatus(text):
	""" Hard codes and returns text as string according to OMIM symbols """
	if text[:2] == "{?":
		return "Mutation contributing to susceptibility to multifactorial disorders or infection. Unconfirmed or possibly spurrious mapping."
	elif text.startswith("{"):
		return "Mutation contributing to susceptibility to multifactorial disorders or infection."
	elif text.startswith("?"):
		return "Unconfirmed or possibly spurrious mapping."
	elif text.startswith("["):
		return "Non-disease. Genetic variation leading to abnormal lab test values."
	else:
		return ""

# 5870 unique disorder nodes total
def writeMIMdisorderNodes(MIMFilePath, mimDisorderNodeOutFile):
	""" Constructs and fills map of disorder information for each node, then iterates and writes to mimDisorderNodeOutFile """
	disorderMap = defaultdict(dict)
	with open(MIMFilePath, 'ru') as inFile:
		count = 0
		for line in inFile:
			columns = line.replace("''", "").replace("'", "prime").split("|")
			geneMIM = columns[2].strip()
			disorderInfo = getDisorderInfo(columns[0].strip(), geneMIM)
			text = disorderInfo[0].lstrip("{").lstrip("[").lstrip("?").rstrip(",").rstrip("}").rstrip("]")
			pheneKey = disorderInfo[-1][1:-1]
			disorderID = disorderInfo[1]
			if not disorderID in disorderMap.keys():
				disorderMap[disorderID]["synonyms"] = set()
				disorderMap[disorderID]["text"] = text
				disorderMap[disorderID]["pheneKey"] = getPheneKey(pheneKey)
			else:
				disorderMap[disorderID]["synonyms"].add(text)
	for k, v in disorderMap.iteritems():
		mimDisorderNode = "%s|OMIM|%s|%s|%s|Phenotype\n" %(k, v["text"], v["pheneKey"], ";".join(v["synonyms"]))
		mimDisorderNodeOutFile.write(mimDisorderNode)
	print "\n\t\t\t\t\t\t%s OMIM disorder/phenotype nodes have been created..." %locale.format('%d', len(disorderMap), True)
			

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

def getDisorderInfo(disorder, geneMIM):
	""" Searches for disorder MIM for disorder MIM node. Uses gene MIM if not found. Returns tuple of text, MIM and phene key """
	found_id = "\d{6}"
	disorderInfo = ""
	found = re.search(found_id, disorder)
	split = disorder.rsplit(" ", 2)
	if found: # contain disorder MIMs
		disorderInfo = (split[0], ("MIM:" + split[1]), split[2])
	else: # does not contain disorder MIMs, use gene MIM
		disorderInfo = ((split[0] + " " + split[1]), ("MIM:" + geneMIM + "p"), split[-1])
	return disorderInfo

def MIMGeneReln(MIMFilePath, mimGeneRelnOutFile):
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
					myKey = (obj.gene_id, "ncbi_entrez_gene", (obj.MIM_id + "p"), "belongs_to")
				elif obj.type == "gene":
					myKey = (obj.gene_id, "ncbi_entrez_gene", obj.MIM_id, "belongs_to")
				relnSet2.add(myKey)
	relnCount = 0
	for reln in relnSet2:
		relnCount += 1
		mimGeneRelnOutFile.write("|".join(reln) + "\n")
	print "\n\t\t\t\t\t  %s OMIM --> NCBI Entrez Gene relationships have been created...\n" %locale.format('%d', relnCount, True)


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
	print "\t\t\t\t * <subdir> : OMIM/"
	print "\t\t\t\t * <subfiles> : *\n"
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

			""" OMIM """
			mimGeneNodeOutFile = open((outPath + 'mimGeneNodeOut.csv'), 'w')
			mimDisorderNodeOutFile = open((outPath + 'mimDisorderNodeOut.csv'), 'w')
			mimRelnOutFile = open((outPath + 'mimRelnOut.csv'), 'w')
			mimGeneRelnOutFile = open((outPath + 'mimGeneRelnOut.csv'), 'w')

			mimGeneNodeOutFile.write("Source_ID:ID|Source|Gene_Symbol:string[]|Cytogenetic_Location|Name|:LABEL\n")
			mimDisorderNodeOutFile.write("Source_ID:ID|Source|Disorder|Status|Synonyms:string[]|:LABEL\n")
			mimRelnOutFile.write(":START_ID|Source|:END_ID|Status|:TYPE\n")
			mimGeneRelnOutFile.write(":START_ID|Source|:END_ID|:TYPE")

			for root, dirs, files in os.walk(topDir):
				
				""" OMIM """
				if root.endswith("OMIM"):
					print "\n\n\n\t\t\t================ PARSING ONLINE MENDELIAN INHERITANCE IN MAN (OMIM) DATABASE ======================"
					print "\n\t\t\t\t\t\t\t\tProcessing files in:"
					for MIMFile in files:
						MIMFilePath =  os.path.join(root, MIMFile)

						if MIMFilePath.endswith("geneMap2.txt"):
							print "\n\t\t\t\t\t\t\t%s" %MIMFilePath
							writeMIMgeneNodes(MIMFilePath, mimGeneNodeOutFile, mimRelnOutFile)
						if MIMFilePath.endswith("morbidmap"):
							print "\n\t\t\t\t\t\t\t%s" %MIMFilePath
							writeMIMdisorderNodes(MIMFilePath, mimDisorderNodeOutFile)
						if MIMFilePath.endswith("mim2gene.txt"):
							print "\n\t\t\t\t\t\t\t%s" %MIMFilePath							
							MIMGeneReln(MIMFilePath, mimGeneRelnOutFile)

			endTime = time.clock()
			duration = endTime - startTime
			print "\n\t\t\t\t\tIt took %s seconds to create all NCBI Taxonomy nodes and relationships\n" %duration

if __name__ == "__main__":
	main(sys.argv[1:])





