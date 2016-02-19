#!/usr/bin/python

import sys
import time
import getopt
import locale
import os
from collections import defaultdict


def parseNodes(ttdFilePath):
	""" Parses TTD_download_raw.txt for node information """

	# nodeDict: when accessing nodeDict[key][key_doesn't_exist], lambda : defaultdict(set) is called
	# and creates nodeDict[key][now_existing_key] = set()
	nodeDict = defaultdict(lambda : defaultdict(set))
	nodeSet = set()
	typeSet = set()
	with open(ttdFilePath, 'rU') as inFile:
		for line in inFile:
			columns = line.strip().split('\t')
			if not len(columns) == 3:
				continue
			else:
				ttdID = columns[0]
				nodeDict[ttdID][columns[1].replace(" ", "_")].add(columns[2])
				nodeSet.add(columns[0])
				typeSet.add(columns[1])
	return nodeDict, nodeSet, typeSet

def writeNodes(nodeDict, nodeOutFile):
	nodeCount = 0
	for k, v in nodeDict.iteritems():
		# print v['Type_of_target']
		nodeString = ('%s|%s|Therapeutic_Target_Database|%s|%s|%s|%s|%s|Protein_Target\n' \
			%(k, "; ".join(v['Name']), "; ".join(v['Function']).replace("|", ""), "; ".join(v['Disease']), "; ".join(v['Synonyms']),
			 "; ".join(v['KEGG_Pathway']), "; ".join(v['Wiki_Pathway'])))
		nodeOutFile.write(nodeString)
		nodeCount += 1
	return nodeCount



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
	cleaned = string.replace(";", ",").replace("|", ";")
	return cleaned

def howToRun():
	""" 
	Instructs users how to use script.
	opts/args: -h, help
	"""
	print "\n\t\t * Run as: python /path/to/this/script.py -p /path/to/top/directory"
	print "\n\t\t * Example top directory: /Users/username/KnowledgeBase/"
	print "\n\t\t * Top directory structure: \n\t\t\t * /Users/username/KnowledgeBase/<subdir>/<files>"
	print "\t\t\t\t * <subdir> : TTD/"
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

			""" Therapeutic Target Database """
			nodeOutFile = open((outPath + 'ttdNodeOut.csv'), 'w')
			relnOutFile = open((outPath + 'ttdRelnOut.csv'), 'w')

			nodeOutFile.write("source_id:ID|Name|Source|Function|Diseases|Synonyms:string[]|KEGG_Pathway|Wiki_Pathway|:LABEL\n")
			# relnOutFile.write(":START_ID|alternate_tax_ids:string[]|source|alternate_gene_ids:string[]|:END_ID|:TYPE\n")
			
			for root, dirs, files in os.walk(topDir):
				
				""" Therapeutic Target Database """
				if root.endswith("TTD"):
					count = 0
					print "\n\n\n\t\t\t================================ PARSING Therapeutic Target Database (TTD) ==================================="
					print "\n\t\t\t\t\t\t\t\tProcessing files in:\n"
					nodeCountList = list()
					nodeList = list()


					for ttdFile in files:
						ttdFilePath = os.path.join(root, ttdFile)
						if ttdFilePath.endswith("TTD_download_raw.txt"):
							print "\t\t\t\t\t\t%s" %ttdFilePath
							nodeDict, nodeSet, typeSet = parseNodes(ttdFilePath)
							print 'nodeSet: ', len(nodeSet), 'typeSet: ', len(typeSet)
							nodeCount = writeNodes(nodeDict, nodeOutFile)
							print nodeCount

							# nodeCount = writeNodes(nodeDict)
							# print nodeCount
						




					endTime = time.clock()
					duration = endTime - startTime
					# print "\n\t\t\t\t\t   %s total NCBI Entrez Gene nodes have been created..." %locale.format('%d', (nodeCountList[0] + nodeCountList[1]), True)
					# print "\n\t\t\t\t\t   %s total NCBI Entrez Gene relationships have been created." %locale.format('%d', (geneGORelnCount + geneTaxRelnCount + geneMIMRelnCount), True)
					# print "\n\t\t\t\t\tIt took %s seconds to create all NCBI Entrez nodes and relationships\n" %duration


if __name__ == "__main__":
	main(sys.argv[1:])

