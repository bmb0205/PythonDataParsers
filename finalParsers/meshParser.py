#!/usr/bin/python

import sys
import os
import getopt
import collections
import locale
import time
import re
from collections import defaultdict

##################################################################################################################
##########################################   MeSH   #########################################################
##################################################################################################################


def parseMeSH(meshFilePath, count, meshNodeOutFile):
	"""
	Creates defaultdict of MeSH block attributes.
	Feeds dict and outfile into writeMeSHNodes() function
	"""
	relnDict = dict()
	with open(meshFilePath, 'ru') as meshFile:
		count = 0
		for block in getBlock(meshFile): # genrator object
			count += 1
			block = block[1:-1]
			myDict = defaultdict(set)
			for attribute in block:
				split = attribute.split(" = ")
				if not len(split) == 1:
					key = split[0]
					value = split[1]
					if key == "MH" or key == "NM" or key == "SH":
						myDict["term"].add(value)
					elif key == "UI":
						myDict["unique_id"].add(value)
					elif key == "MH" or key == "RN" or key == "NM":
						myDict["synonyms"].add(value)
					elif key == "MN":
						myDict["mesh_tree_number"].add(value)
					elif key == "ST":
						myDict["semantic_type"].add(value)
					elif key == "ENTRY" or key == "PRINT ENTRY" or key == "SY":
						split_value = value.split("|")
						header = split_value[-1]
						if len(split_value) == 1:
							myDict["synonyms"].add(split_value[0])
						else:
							myDict["synonyms"].add(split_value[0])
							headerIndex = header.index("d")
							semanticRelationship = split_value[headerIndex]
							myDict["semantic_relationship"].add(semanticRelationship)
			unique = "".join(myDict['unique_id'])
			treeNums = myDict['mesh_tree_number']
			if len(treeNums) != 0:
				relnDict[unique] = treeNums
			writeMeSHNodes(myDict, meshNodeOutFile)
	return count, relnDict

			# synonyms include: MH, ENTRY(take first field as synonym(a)...also take semantic relation(d), SY, NM, RN
			# mesh tree number MN for relationships, download MeSH tree

def getBlock(meshFile):
	""" Yields generator object for each new entry """
	block = []
	blockDict = defaultdict(set)
	for line in meshFile:
		if line.startswith("*NEWRECORD"):
			if block:
				yield block
			block = []
		if line:
			block += [line.strip()]
	if block:
		yield block
			

def writeMeSHNodes(myDict, meshNodeOutFile):
	"""  """
	keyList = ["unique_id", "term", "synonyms", "semantic_type", "mesh_tree_number"]
	for item in keyList:
		if not item in myDict.keys():
			myDict[item] = ""
	node = "%s|MeSH|%s|%s|%s|%s|MedicalHeading\n" %(";".join(myDict["unique_id"]), ";".join(myDict["term"]), ";".join(myDict["synonyms"]), ";".join(myDict["semantic_type"]), ";".join(myDict["mesh_tree_number"]))
	meshNodeOutFile.write(node)

def parseTree(meshFilePath, myDict, meshRelnOutFile):
	""" Parses MeSH Tree for relationships """
	treeMap = defaultdict(set)
	aList = list()
	aMap = dict()
	with open(meshFilePath, 'rU') as inFile:
		for line in inFile:
			heading, treeNumber = line.strip().split(';')
			if treeNumber.startswith('A'):
				aMap[treeNumber] = heading
				treeMap['A'].add((heading, treeNumber))
				aList.append(treeNumber)
			elif treeNumber.startswith('B'):
				treeMap['B'].add((heading, treeNumber))
	# for item in myDict.items():
	# 	print item
	# aList.sort(key = len)
	# for item in aList:
	# 	itemType = "Anatomy"
		# if item.startswith('A01'):
		# 	print item, '\t', itemType, '\t', aMap[item]
	# for k, v in treeMap.iteritems():
	# 	print k, '\n' # "A"
	# 	for k1, k2 in v:
	# 		if k2 == 'A01':
	# 			print "Top node: ", k2, "  ", k1
	# 		elif k2.startswith('A01.'):
	# 			print "\t", k2, "  ", k1



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
	print "\t\t\t\t * <subdir> : MeSH/"
	print "\t\t\t\t * <subfiles> : *.bin\n"
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

			meshNodeOutFile = open((outPath + 'meshNodeOut.csv'), 'w')
			meshRelnOutFile = open((outPath + 'meshRelnOut.csv'), 'w')
			meshNodeOutFile.write("source_id:ID|source|term|synonyms:string[]|semantic_type:string[]|mesh_tree_number|:LABEL\n")
			# meshRelnOutFile.write()

			for root, dirs, files in os.walk(topDir):

				""" MESH """
				if root.endswith("MeSH"):
					print "\n\n\n\t\t================================ PARSING NLM MEDICAL SUBJECT HEADINGS (MeSH) DATABASE ================================"
					print "\n\t\t\t\t\t\t\t\tProcessing files in:\n"
					startTime = time.clock()
					finalCount = 0
					count = 0
					bigRelnDict = dict()
					sortedFiles = sorted(files, key=len)
					for meshFile in sortedFiles:#.sort(key = len):
						meshFilePath = os.path.join(root, meshFile)
				 		# print "    \t\t\t\t\t\t%s" %meshFilePath
				 		if not meshFilePath.endswith("mtrees2015.bin"):
							count, relnDict = parseMeSH(meshFilePath, count, meshNodeOutFile)
							bigRelnDict.update(relnDict)
							finalCount += count
						else:
							parseTree(meshFilePath, bigRelnDict, meshRelnOutFile)

						# print "\n\t\t\t\t\t\t\t%s nodes have been created from this file\n" %locale.format('%d', count, True)
					# endTime = time.clock()
					# duration = endTime - startTime
					# print "\n\t\t\t\t\t\t    %s total NLM MeSH nodes have been created..." %locale.format('%d', finalCount, True)
					# print "\n\t\t\t\t\t\t  It took %s seconds to create all NLM MeSH nodes\n" %duration

if __name__ == "__main__":
	main(sys.argv[1:])