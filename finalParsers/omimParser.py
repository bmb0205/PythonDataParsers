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
	with open(MIMFilePath, 'ru') as inFile:
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
	# mySet = set()
	count = 0


	# for k, v in nodeMap.iteritems():
	# 	print k, vars(v), '\n'

	# print len(nodeSet), type(nodeSet), '\n'
	# for node in nodeSet: # nodeSet is set of MIMNode objects from geneMap2...may have dup
	# 	nodeAttr = vars(node)
	# 	if not node.gene_id in mySet:
	# 		mySet.add(node.gene_id)



	##### have nodeMap genenodeid : geneNodeObj
		# print attr['name'], '\t', attr['disorder_info']
	with open(MIMFilePath, 'ru') as inFile:
		# print len(uniqueSet) 6657
		for line in inFile:
			columns = line.replace("''", "").replace("'", "prime").split("|")
			disObj = DisorderNode(columns)
			myTup = (disObj.disorderID, disObj.pheneKey, disObj.geneMIM) # reln
			disorderMap[disObj.disorderID].add(disObj)
	
	for k, v in disorderMap.iteritems():
		myList = list()
		synonymSet = set()
		print '\n\n', k
		if len(v) > 1:
			for item in v:
				textPhene = (item.pheneKey, item.text)
				if not textPhene in myList:
					myList.append(textPhene)
			sortedList = sorted(myList, key = itemgetter(0))
			if sortedList:
				text = sortedList[-1][1]
				pheneKey = getPheneKey(sortedList[-1][0])
				other = sortedList[:-1]
				for item in other:
					synonymSet.add(item[1])
				# print text, '\n', ";".join(synonymSet)
				mimDisorderNode = "%s|OMIM|%s|%s|Phenotype\n" %(k, text, ";".join(v["synonyms"]))
				mimDisorderNodeOutFile.write(mimDisorderNode)
		else:
			print v
			# mimDisorderNode = "%s|OMIM|%s|%s|Phenotype\n" %(k, (";".join(v)).text, "")
			# mimDisorderNodeOutFile.write(mimDisorderNode)


	# print count

	# for k, v in disorderMap.iteritems():
	# 	newSet = set()
	# 	print '\n\n', k
	# 	for item in v:
	# 		newSet.add(item[-1])
	# 	if len(newSet) > 1:
	# 		for item in v:
	# 			print item


			# print vars(disObj)['disorderID'], vars(disObj), '\n'
			# if disObj.disorderID in nodeMap.keys():# or (disObj.disorderID + 'p') in nodeMap.keys():
			# 	print disObj.disorderID, '\n', vars(disObj), '\n', vars(nodeMap[disObj.disorderID]), '\n\n'
			# alt = disObj.disorderID + 'p'
			# if alt in nodeMap.keys():
			# 	print alt, '\n', vars(disObj), '\n', vars(nodeMap[alt]), '\n\n'

			# 	print disObj.disorderID
			# 	alt = disObj.disorderID + 'p'
			# 	print alt, '\n'
			# 	nodeMap[alt] = disObj
			# else:
			# 	nodeMap[disObj.disorderID] = disObj
			# else:
			# 	print 'ol', disObj.disorderID
			# geneMIM = columns[2].strip()
			# disorderInfo = getDisorderInfo(columns[0].strip(), geneMIM)
			# print 'disorderInfo:', disorderInfo
			# text = disorderInfo[0].lstrip("{").lstrip("[").lstrip("?").rstrip(",").rstrip("}").rstrip("]")
			# pheneKey = disorderInfo[-1][1:-1]
			# disorderID = disorderInfo[1]
			# print 'disorderID:', disorderID
			# alt = disorderID + 'p'
			# if not disorderID in nodeMap:
			# 	nodeMap[disorderID] = 
			# else:
			# 	print disorderID, nodeMap[disorderID]



# 				"""
# 				# print disorderInfo, '\n', vars(nodeMap[disorderID]), '\n\n'
# 				disorderMap[disorderID]["synonyms"] = set()
# 				disorderMap[disorderID]["text"] = text
# 				disorderMap[disorderID]["pheneKey"] = getPheneKey(pheneKey)

# 			# if not disorderID in disorderMap.keys(): # unseen
# 			# 	disorderMap[disorderID]["synonyms"] = set()
# 			# 	disorderMap[disorderID]["text"] = text
# 			# 	disorderMap[disorderID]["pheneKey"] = getPheneKey(pheneKey)
# 				# print 'first', disorderMap[disorderID], '\n'
# 			else: # seen
# 				if not "synonym" in disorderMap[alt]:
# 					disorderMap[alt]["synonyms"] = set()
# 				else:
# 					disorderMap[alt]["synonyms"].add(text)
# 				disorderMap[alt]["text"] = text
# 				disorderMap[alt]["pheneKey"] = getPheneKey(pheneKey)
# 				# print 'duplicate', disorderID, disorderMap[disorderID], '\n'
# 			# print disorderMap[disorderID], '\n\n'
# 	# count2 = 0


# 	for k, v in disorderMap.iteritems():
# 		# if len(v['synonyms']) != 0:
# 		print k, v
# """
	# print len(nodeMap)
	# for k, v in nodeMap.iteritems():
	# 	print k, vars(v), '\n'
	# 	if not k in disorderMap.keys():
	# 		print 'lol'
	# 	else:

	# for k, v in disorderMap.iteritems():
	# 	if not k in nodeMap.keys():
	# 		mimDisorderNode = "%s|OMIM|%s|%s|%s|Phenotype\n" %(k, v["text"], v["pheneKey"], ";".join(v["synonyms"]))
	# 		mimDisorderNodeOutFile.write(mimDisorderNode)
	# 	else: #57...already a node of same ID from geneMap2
	# 		# newSet.

	# 		mimDisorderNode2 = "%s|OMIM|%s|%s|%s|Phenotype\n" %(k+'p', v["text"], v["pheneKey"], ";".join(v["synonyms"]))
	# 		mimDisorderNodeOutFile.write(mimDisorderNode2)

			# print k, v, '\n\n'
			# mimDisorderReln = "%s|OMIM|%s|phenotype_of\n" %(k, nodeMap)
			# mimDisorderRelnOutFile.write(mimDisorderReln)

			# print "disorders", k, disorderMap[k], '\n already here in genes:', nodeMap[k].gene_id, vars(nodeMap[k]), '\n'
			# print disorderMap['MIM:603013'], '\n\n'

# 		"""
# 		yep didn't quite get it lol so here is a clear example of a duplicate again
# [2/11/16, 5:17 PM] Brandon Burciaga (bburciag@uncc.edu): MIM:614322p|OMIM|Spinocrebellar ataxia, autosomal recessive 12|Disorder has known molecular basis. Mutation found.||Phenotype
# [2/11/16, 5:17 PM] Brandon Burciaga (bburciag@uncc.edu): it wants to write that^^
# [2/11/16, 5:17 PM] Brandon Burciaga (bburciag@uncc.edu): but this is already written:
# [2/11/16, 5:17 PM] Brandon Burciaga (bburciag@uncc.edu): csv_out/mimDisorderNodeOut.csv:MIM:614322p|OMIM|Spinocerebellar ataxia, autosomal recessive 12|Disorder placed by linkage. No mutation found.||Phenotype
# [2/11/16, 5:18 PM] Brandon Burciaga (bburciag@uncc.edu): and the source lines they are from:
# [2/11/16, 5:19 PM] Brandon Burciaga (bburciag@uncc.edu): OMIM/morbidmap:Spinocerebellar ataxia, autosomal recessive 12 (2)|SCAR12|614322|16q21-q23
# OMIM/morbidmap:Spinocrebellar ataxia, autosomal recessive 12, 614322 (3)|WWOX, FOR, SCAR12, EIEE28|605131|16q23.1-q23.2
# [2/11/16, 5:19 PM] Brandon Burciaga (bburciag@uncc.edu): so I don't even remember if we answered this but how do you want to handle them/join them?

# 		"""
# 			count2 += 1
# 			# print k + 'p'
# 			mimDisorderNode = "%s|OMIM|%s|%s|%s|Phenotype\n" %(k+'p', v["text"], v["pheneKey"], ";".join(v["synonyms"]))
# 			print mimDisorderNode
# 			# mimDisorderNodeOutFile.write(mimDisorderNode)
# 			mySet.add(k + 'p')
# 			# print k, '\t', v
# 	print len(mySet), count2
# 	print mySet
# 	print "\n\t\t\t\t\t\t%s OMIM disorder/phenotype nodes have been created..." %locale.format('%d', len(disorderMap), True)

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
