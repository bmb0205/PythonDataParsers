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
def writeMIMgeneNodes(MIMFilePath, mimGeneNodeOutFile, mimGeneRelnOutFile): # MIM/geneMap2.txt
	"""	writes MIM gene nodes to mimGeneNodeOutFile, writes MIM relationships to mimRelnOutFile """
	nodeCount = 0
	relnCount = 0
	uniqueSet = set()
	nodeSet = set()
	nodeMap = dict()
	count = 0
	with open(MIMFilePath, 'ru') as inFile: #15,755 gene nodes
		for line in inFile:
			nodeCount += 1
			columns = line.replace("''", "").replace("'", "prime").split("|")
			obj = MIMNode(columns)
			mimGeneNode = "%s|OMIM|%s|%s|%s|Gene\n" %(obj.gene_id, obj.getGeneSymbols(), obj.cytogenetic_location, obj.name)
			mimGeneNodeOutFile.write(mimGeneNode)
			nodeMap[obj.gene_id] = obj
			# print vars(obj)
			nodeSet.add(obj.gene_id)
			if not obj.disorder_info == "": # 4786 genes associated with disorders
				relnSet = obj.getDisorderInfo()
				# print '\n', obj.gene_id
				# obj.getDisorderInfo()
				# print obj.gene_id, relnSet, '\n'


				"""

				As of friday 3pm nodes seemingly done for disorder and gene, working on relns


				"""
				for reln in relnSet:
					myTup = (obj.gene_id, reln[2], reln[1])
					# print myTup
					if not myTup in uniqueSet:
						uniqueSet.add(myTup)
					else:
						# print 'dup', myTup, line, '\n'
						count += 1
					# # print 'lol', reln
		 		# 	status = getStatus(reln[0])
		 		# 	uniqueSet.add(myTup) # (geneMIM, pheneKey, pheneMIM)
					# mimGeneReln = "%s|OMIM|%s|%s|causes_phenotype\n" %(obj.gene_id, reln[1], status)
		 		# 	mimGeneRelnOutFile.write(mimGeneReln)
	print len(nodeMap), len(uniqueSet), '\n\n'



					# if not reln[1] in uniqueSet:
			# 			relnCount += 1
			# 			uniqueSet.add(reln[1])
			# 			# print reln
			# 			status = getStatus(reln[0])
			# 			mimGeneReln = "%s|OMIM|%s|%s|causes_phenotype\n" %(obj.gene_id, reln[1], status)

			# 			#!!#!! reverse relationships?

			# 			mimGeneRelnOutFile.write(mimGeneReln)
			# else:
			# 	continue
	print "\n\t\t\t\t\t\t\t%s OMIM gene nodes have been created..." %locale.format('%d', nodeCount, True)
	print "\n\t\t\t\t\t\t\t%s OMIM relationships have been created...\n" %locale.format('%d', relnCount, True)
	return nodeMap, nodeSet, uniqueSet

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
def writeMIMdisorderNodes(MIMFilePath, mimDisorderNodeOutFile, mimDisorderRelnOutFile, nodeMap, nodeSet, uniqueSet):
	""" Constructs and fills map of disorder information for each node, then iterates and writes to mimDisorderNodeOutFile """
	disorderMap = defaultdict(set)
	with open(MIMFilePath, 'ru') as inFile:
		for line in inFile:
			columns = line.replace("''", "").replace("'", "prime").split("|")
			disObj = DisorderNode(columns)
			myTup = (disObj.disorderID, disObj.pheneKey, disObj.geneMIM) # reln
			disorderMap[disObj.disorderID].add(disObj)
			
	# print 'disorder map:', len(disorderMap) # 5848 disorder nodes total.....
	# 1167 duplicates spread over 544 nodes (some have more than 1 duplicate)

	for k, v in disorderMap.iteritems():
		myList = list()
		synonymSet = set()
		if len(v) > 1: # 544 nodes with at least one duplicate...take best pheneKey and text, other text are synonyms
			bcount += 1
			for obj in v:
				textPhene = (obj.pheneKey, obj.text)
				if not textPhene in myList:
					myList.append(textPhene)
			sortedList = sorted(myList, key = itemgetter(0))
			# if sortedList:
			text = sortedList[-1][1]
			pheneKey = getPheneKey(sortedList[-1][0])
			other = sortedList[:-1]
			for item in other:
				synonymSet.add(item[1])
			mimDisorderNode = "%s|OMIM|%s|%s|Phenotype\n" %(k, text, ";".join(synonymSet))
			mimDisorderNodeOutFile.write(mimDisorderNode)
		else: # 5304 nodes with no duplicates
			count += 1
			obj = v.pop()
			mimDisorderUniqueNode = "%s|OMIM|%s|%s|Phenotype\n" %(k, obj.text, "")
			mimDisorderNodeOutFile.write(mimDisorderUniqueNode)

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
			
			mimGeneRelnOutFile = open((outPath + 'mimGeneRelnOut.csv'), 'w')
			mimDisorderRelnOutFile = open((outPath + 'mimDisorderRelnOut.csv'), 'w')

			mimEntrezRelnOutFile = open((outPath + 'mimEntrezRelnOut.csv'), 'w')

			mimGeneNodeOutFile.write("Source_ID:ID|Source|Gene_Symbol:string[]|Cytogenetic_Location|Name|:LABEL\n")
			mimDisorderNodeOutFile.write("Source_ID:ID|Source|Disorder|Synonyms:string[]|:LABEL\n")
			
			mimGeneRelnOutFile.write(":START_ID|Source|:END_ID|Status|:TYPE\n")
			mimDisorderRelnOutFile.write(":START_ID|Source|:END_ID|Status|:TYPE\n")

			mimEntrezRelnOutFile.write(":START_ID|Source|:END_ID|:TYPE")

			uniqueSet = set()
			for root, dirs, files in os.walk(topDir):
				
				""" OMIM """
				if root.endswith("OMIM"):
					print "\n\n\n\t\t\t================ PARSING ONLINE MENDELIAN INHERITANCE IN MAN (OMIM) DATABASE ======================"
					print "\n\t\t\t\t\t\t\t\tProcessing files in:"
					for MIMFile in files:
						MIMFilePath =  os.path.join(root, MIMFile)

						if MIMFilePath.endswith("geneMap2.txt"):
							print "\n\t\t\t\t\t\t\t%s" %MIMFilePath
							nodeMap, nodeSet, uniqueSet= writeMIMgeneNodes(MIMFilePath, mimGeneNodeOutFile, mimGeneRelnOutFile)
						if MIMFilePath.endswith("morbidmap"):
							print "\n\t\t\t\t\t\t\t%s" %MIMFilePath
							writeMIMdisorderNodes(MIMFilePath, mimDisorderNodeOutFile, mimDisorderRelnOutFile, nodeMap, nodeSet, uniqueSet)
						if MIMFilePath.endswith("mim2gene.txt"):
							print "\n\t\t\t\t\t\t\t%s" %MIMFilePath							
							MIMGeneReln(MIMFilePath, mimEntrezRelnOutFile)

			endTime = time.clock()
			duration = endTime - startTime
			print "\n\t\t\t\t\tIt took %s seconds to create all NCBI Taxonomy nodes and relationships\n" %duration

if __name__ == "__main__":
	main(sys.argv[1:])
