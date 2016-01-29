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
from omimClasses import MorbidMap
from omimClasses import MIMToGene




"""
Main file parser used to parse and extract data from NCBI Entrez Gene, MeSH and OMIM databases.
Parsed information is written to pipe delimited .csv outfiles in a directory created by the script.
See howToRun() method below for help running script.
Written by: Brandon Burciaga
"""



##################################################################################################################
#########################################   MIM   ###########################################################
##################################################################################################################


# 4786 genes associated with disorders
def writeMIMgeneNodes(MIMFilePath, mimGeneNodeOutFile): # MIM/geneMap2.txt
	"""	writes MIM nodes to MIMOutFile """
	# geneDisorderMap = dict()
	# geneSet = set()
	testSet = set()
	with open(MIMFilePath, 'ru') as inFile:
		# 15,705 unique MIM numbers (no duplicate lines) 
		for line in inFile:
			columns = line.replace("''", "").replace("'", "prime").split("|")
			obj = MIMNode(columns)

			print '\n'
			print obj.gene_id
			if not obj.disorder_info == "":
				found_id = "\d{6}"


				# pheneList = re.findall(found_id, obj.getDisorderMIM())
				# pheneSet = set(pheneList)
				# obj.getDisorderMIM()
				# print obj.gene_id
				relnSet = obj.getDisorderMIM()
				print relnSet
			else:
				print 'no disorders'
				# print '\n\n'#, "\ngene mim: ", obj.gene_id, '\n\npheneSet: ', pheneSet, '\n\ngetDisorderMimAndTexT: ', obj.getDisorderTextAndMIM(), '\n\n', line, '\n\n\n'
	# 			pheneTextList = re.findall(";", obj.getDisorderMIM())

	# 			# print "len pheneList", len(pheneSet)
	# 			# print "len phene text", (len(pheneTextList) + 1)
	# 			# print obj.gene_id, pheneList

	# 			# for phene in pheneList: # adds relns that map back to themselves due to missing pheneMIM
	# 			# 	if obj.gene_id[3:] == phene:
	# 			# 		geneSet.add((obj.gene_id, "OMIM", (phene+"P"), "associated_with"))

	# 			# if len(pheneList) != (len(pheneTextList)+1):
	# 			# 	diff = (len(pheneTextList)+1) - len(pheneList)



	# 				# print obj.getDisorderMIM()
	# 				# print diff, obj.gene_id, pheneList, '\n'


	# 				# print len(pheneList), (len(pheneTextList)+1), obj.getDisorderMIM(), '\n'
				

	# 			for phene in pheneSet:
	# 				pheneID = ("MIM:" + phene)
	# 				if not obj.gene_id == pheneID:
	# 					geneSet.add((obj.gene_id, "OMIM", pheneID,  "associated_with"))
	# 				else:
	# 					geneSet.add((obj.gene_id, "OMIM", (pheneID+"P"),  "associated_with"))
	# 			# geneDisorderMap[obj.gene_id] = obj.getDisorderInfo() # for relationships
			
	# 		mimGeneNode = "%s|OMIM|%s|%s|%s|Gene\n" %(obj.gene_id, obj.getGeneSymbols(), obj.cytogenetic_location, obj.title)
	# 		mimGeneNodeOutFile.write(mimGeneNode)
	# 		count += 1
	# return count, geneDisorderMap, geneSet



# 5561 with disorder mim num vs 1422 without disorder MIM num
def writeMIMdisorderNodes(MIMFilePath, mimDisorderNodeOutFile, geneDisorderMap, geneSet):
	""" """
	mySet = set()
	mySet2 = set()
	disDict= dict()
	with open(MIMFilePath, 'ru') as inFile:
		count = 0
		for line in inFile:
			columns = line.replace('"', "").replace("'", '').replace(";", ",").split("|")
			obj = MorbidMap(columns)


			found_id = "\d{6}"
			phene = re.search(found_id, obj.disorder_text)
			if phene:
				geneSet.add((("MIM:" + phene.group(0)), "OMIM", obj.geneMIM, "associated_with"))

			# if not obj.geneMIM in mySet:
			# 	mySet.add(obj.geneMIM)
			# 	disDict= {'': {'synonyms': set(), 'status': ''}}
			# 	disDict[obj.geneMIM]['synonyms'].add(obj.getDisorderText())
			# 	distDict[obj.geneMIM]['status'] = obj.getPheneKey()
			# else:
			# 	disDict[obj.geneMIM]['synonyms'].add(obj.getDisorderText())
			# 	disDict[obj.geneMIM]['status'] = obj.getPheneKey()


			mimDisorderNode = "%s|OMIM|%s|%s|Phenotype\n" %(obj.getPheneMIM(), obj.getDisorderText(), obj.getPheneKey())
			mimDisorderNodeOutFile.write(mimDisorderNode)			
	for item in disDict.items():
		print item
	print len(disDict)
	return count, geneSet

def MIMGeneReln(MIMFilePath, geneMIMRelnOutFile):
	""" """
	relnSet2 = set()
	with open(MIMFilePath, 'ru') as inFile:
		for line in inFile:
			columns = line.strip().split('\t')
			obj = MIMToGene(columns)
			if not obj.getGeneID() == "":
				myKey = (obj.getGeneID(), "ncbi_entrez_gene", obj.MIM_id, "belongs_to")
				relnSet2.add(myKey)
	for reln in relnSet2:
		geneMIMRelnOutFile.write("|".join(reln) + "\n")

def writeMIMRelationships(geneSet, mimRelnOutFile):
	""" """
	for reln in geneSet:
		mimRelnOutFile.write("|".join(reln) + "\n")


	# print len(geneDisorderMap)
	# for k, v in geneDisorderMap.iteritems():
	# 	found_id = "\d{6}"
	# 	idList = re.findall(found_id, v)
	# 	if idList:
	# 		for ID in idList:
	# 			ID = "MIM:" + ID
	# 			mySet.add((k, ID))
	# for item in mySet:
	# 	reln = "%s|MIM|%s|causes_phenotype\n" %(item[0], item[1])
	# 	mimRelnOutFile.write(reln)

	# match unqiue IDs to gene symbols from disorde -> gene


# if disorder MIM is included in line...disorder MIM = phenotype MIM....gene MIM different
# if disorder MIM not included in line, gene MIM = phenotype MIM



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

			""" OMIM """
			mimGeneNodeOutFile = open((outPath + 'mimGeneNodeOut.csv'), 'w')
			mimDisorderNodeOutFile = open((outPath + 'mimDisorderNodeOut.csv'), 'w')
			mimRelnOutFile = open((outPath + 'mimRelnOut.csv'), 'w')

			mimGeneNodeOutFile.write("Source_ID:ID|Source|Gene_Symbol:string[]|Cytogenetic_Location|Title|:LABEL\n")
			mimDisorderNodeOutFile.write("Source_ID:ID|Source|Disorder|Status|:LABEL\n")
			mimRelnOutFile.write(":START_ID|Source|:END_ID|:TYPE\n")

			for root, dirs, files in os.walk(topDir):
				
				""" OMIM """
				if root.endswith("OMIM"):
					print "\n\n\n\t\t\t================ PARSING ONLINE MENDELIAN INHERITANCE IN MAN (OMIM) DATABASE ======================"
					print "\n\t\t\t\t\t\t\t\tProcessing files in:"
					for MIMFile in files:
						MIMFilePath =  os.path.join(root, MIMFile)

						if MIMFilePath.endswith("geneMap2.txt"):
							print "\n\t\t\t\t%s" %MIMFilePath
							writeMIMgeneNodes(MIMFilePath, mimGeneNodeOutFile)
							# count, geneDisorderMap, geneSet = writeMIMgeneNodes(MIMFilePath, mimGeneNodeOutFile)
							# writeMIMRelationships(geneDisorderMap, mimRelnOutFile)
						# if MIMFilePath.endswith("morbidmap"):
						# 	count, geneSet = writeMIMdisorderNodes(MIMFilePath, mimDisorderNodeOutFile, geneDisorderMap, geneSet)
						# 	writeMIMRelationships(geneSet, mimRelnOutFile)
						# if MIMFilePath.endswith("mim2gene.txt"):
						# 	mimGeneRelnSet = MIMGeneReln(MIMFilePath, geneMIMRelnOutFile)


if __name__ == "__main__":
	main(sys.argv[1:])





