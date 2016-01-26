#!/usr/bin/python

import sys
import os
import getopt
import locale
import re
import time
from collections import defaultdict


"""
##################################################################################################################
########################   National Agricultural Library Thesaurus Parser   ######################################
##################################################################################################################

Parses National Agricultural Library thesaurus for graph database node and relationship creation.
See howToRun() method for instructions.
Infile(s): NAL Thesaurus 2015 (*.xml)
Outfile(s): nalNodeOut.csv

"""

def getBlock(nalFile):
	""" Generator function which yields <CONCEPT> blocks """
	block = []
	for line in nalFile:
		line = line.strip()
		if line.startswith("<!") or line.startswith("<?") or line == "<THESAURUS>":
			continue
		if line.startswith("<CONCEPT>"):
			if block:
				yield block
			block = []
		if line and line != "</CONCEPT>":
			block += [line]
	if block:
		yield block

def parseNAL(blockList, nalMap):
	"""
	Populates nalMap with the key being the unique NAL ID and the value being 
	a defaultdict(str) of attributes of each block.
	Adds "UF" myDict key to set for synonyms.
	"""
	mySet = set()
	count = 0
	for block in blockList:
		count += 1
		myDict = defaultdict(str)
		myDict["UF"] = set()
		for item in block[1:]:
			temp = re.split(">", item)[0]
			key = temp[1:]
			match = re.search(">(.+)<", item)
			if match:
				if key == "UF":
					myDict["UF"].add(match.group(1))
				else:
					myDict[key] = match.group(1)
			uniqueID = "NAL:" + myDict["TNR"]
			nalMap[uniqueID] = myDict
	return nalMap

def writeNodes(nalMap, nalNodeOutFile):
	""" Iterates nalMap, calls desired attributes and writes node to outfile """
	for uniqueID, attributes in nalMap.iteritems():
		node = "%s|National_Agricultural_Library|%s|%s|%s|Plant\n" %(uniqueID, attributes["DESCRIPTOR"], attributes["SC"], ";".join(attributes["UF"]))
		nalNodeOutFile.write(node)				


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
    print "\t\t\t\t * <subdir> : NAL/"
    print "\t\t\t\t * <subfiles> : *.xml\n"
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

			nalNodeOutFile = open((outPath + "nalNodeOut.csv"), 'w')
			nalRelnOutFile = open((outPath + "nalRelnOut.csv"), 'w')
			nalRoot = topDir + "NAL/"

			nalNodeOutFile.write("source_id:ID|source|descriptor|subject_category|synonyms:string[]|LABEL:\n")

			print "\n\n\n\t\t\t\t===================  PARSING National Agricultural Library Thesaurus ====================="
			print "\n\t\t\t\t\t\t\t\t\tProcessing files in:\n\n\t\t\t\t\t\t\t\t    %s\n" % nalRoot
			print "\n\t\t\t\t\t\t\t\t\t Files processed: "

			nalMap = defaultdict(dict)
			for root, dirs, files in os.walk(topDir):
				if root.endswith("NAL"):
					for nalFile in files:
						if nalFile.endswith(".xml"):
							nalFilePath = os.path.join(root, nalFile)
							print "\n\t\t\t\t\t\t\t %s " %nalFilePath
							with open(nalFilePath, 'ru') as inFile:
								blockList = getBlock(inFile)
								nalMap = parseNAL(blockList, nalMap)
								print "\n\t\t\t\t\t\t%s National Agricultural Library nodes have been created...\n" %locale.format('%d', len(nalMap), True)
			writeNodes(nalMap, nalNodeOutFile)
			endTime = time.clock()
			duration = endTime - startTime
			print "\t\t\t\t\t\tIt took %s seconds to parse the files and create all NAL nodes \n" %duration

if __name__ == "__main__":
	main(sys.argv[1:])