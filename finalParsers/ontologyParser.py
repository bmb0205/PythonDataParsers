#!/usr/bin/python

import sys
import getopt
import os
import re
import time
import locale
import itertools
from collections import defaultdict
from ontologyClasses import OntologyParser

"""
##################################################################################################################
##########################################   Ontology Parser   #########################################################
##################################################################################################################

Written by: Brandon Burciaga

* Parses files from multiple ontologies for neo4j graph database node and relationship creation.
* Outfiles are .csv (pipe delimited) and generated with first line header of 
	node IDs, attributes, types and labels for neo4j-import tool
* See howToRun() method for instructions using this script.
* Infile(s) [ontology files in .obo format, 2015 versions used]:
	* CHEBI Ontology, https://www.ebi.ac.uk/chebi/downloadsForward.do
	* Disease Ontology, http://disease-ontology.org/downloads/
	* Gene Ontology, http://geneontology.org/page/download-ontology
	* Human Phenotype Ontology, http://human-phenotype-ontology.github.io/downloads.html
	* Mammalian Phenotype Ontology, http://obofoundry.org/ontology/mp.html
	* Gene Ontology --> CHEBI Ontology, http://geneontology.org/
	* Plant Ontoogy, Plant Trait Ontology, http://www.plantontology.org/download
* Outfile(s): GOmfbp_to_ChEBI.csv, MPheno.ontology.csv, chebi_ontology.csv, disease_ontology.csv, gene_ontology.csv,
	human_phenotype.csv, molecular_function_xp_chebi.csv, plant_trait_ontology.csv
* Imports: ontologyClasses.py module

"""

def getBlock(oboFile):
	""" Generator function which yields .obo blocks """
	block = []
	for line in oboFile:
		line = line.strip()
		if line.startswith("["):
			if block:
				yield block
			block = []
		if line:
			block += [line]
	if block:
		yield block

def sortBlocks(blockList):
	""" Sorts blocks into metadeta, terms, and typedefs """
	metaData = list()
	termList = list()
	typedefList = list()
	for block in blockList:
		blockType = block[0]
		if blockType == "format-version: 1.2":
			metaData.append(block)
		elif blockType == "[Term]":
			del block[0]
			termList.append(block)
		else:
			del block[0]
			typedefList.append(block)
	return termList, typedefList, metaData

def getSource(metaData):
	""" Returns source of file being parsed """
	if metaData:
		metaData = metaData[0]
		for line in metaData:
			headerStanza = line.split(": ",1)
			if headerStanza[0] == "default-namespace":
				source = headerStanza[1].strip()
				return source

def editSource(mySource, oboFilePath):
	""" Edits source of data to more readable format """
	editedSource = ""
	if mySource is None:
		if oboFilePath.endswith("GOmfbp_to_ChEBI03092015.obo"):
			editedSource = "GOtoCHEBI_ontology"
		else:
			editedSource = "molecular_function_xp_CHEBI_ontology"
	else:
		if mySource.endswith("plant_ontology.obo"):
			editedSource = "plant_ontology"
		elif mySource.endswith("MPheno.ontology"):
			editedSource = "mammalian_phenotype_ontology"
		else:
			editedSource = mySource
	return editedSource

def parseTagValue(block):
	""" Creates tag, value dictionary to set up parsing """
	data = defaultdict(list)
	for item in block:
		if "(Spanish)" in item or "(Japanese)" in item or "!!!" in item:
			continue
		tag = item.split(": ")[0]
		value = item.split(": ", 1)[1]
		data[tag].append(value)
	return data

def writeNodes(nodeOutFile, nodeSet):
	""" Writes ontology nodes using attributes listed """
	nodeCount = 0
	with open(nodeOutFile, "w") as oboNodeOut:
		oboNodeOut.write("Source_ID:ID|Name|Source|Definition|Synonyms:string[]|:LABEL\n")
		for node in nodeSet:
			node = clean(node)
			nodeCount += 1
			oboNodeOut.write(node)
	return nodeCount

def writeRelationships(relnOutFile, uniqueNodeSet, relnSet):
	""" 
	Writes header and relationships to oboRelnOut.csv if the nodes exist.
	Writes bad relationships to outfile.
	"""
	relnCount = 0
	badRelnOutFile = relnOutFile.rsplit("/", 1)[0] + "/badOntologyReln.csv"
	with open(relnOutFile, "w") as oboRelnOut, open(badRelnOutFile, "w") as badOntologyRelnOut:
		oboRelnOut.write(":START_ID|Source|:END_ID|:TYPE\n")
		badOntologyRelnOut.write("# relationships with at least one missing node\n")
		for reln in relnSet:
			reln1 = reln.split("|")[0]
			reln2 = reln.split("|")[2]
			if reln1 in uniqueNodeSet and reln2 in uniqueNodeSet:
				relnCount += 1
				reln = clean(reln)
				oboRelnOut.write(reln + "\n")
			else: # skips relationships due to nodes not existing
				if not reln1 in uniqueNodeSet:
					badOntologyRelnOut.write(reln + "\t\tMissing node:  " + reln1 + '\n')                    
				elif not reln2 in uniqueNodeSet:
					badOntologyRelnOut.write(reln + "\t\tMissing node:  " + reln2 + '\n')
	return relnCount

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
	""" Cleans lines of any characters that may affect neo4j database creation or import """
	cleaned = string.replace("'", "").replace('"', '')
	return cleaned

def howToRun():
	""" 
	Instructs users how to use script.
	opts/args: -h, help
	"""
	print "\n\t\t * Run as: python /path/to/this/script.py -p /path/to/top/directory"
	print "\n\t\t * Example top directory: /Users/username/KnowledgeBase/"
	print "\n\t\t * Top directory structure: \n\t\t\t * /Users/username/KnowledgeBasedDiscovery/<subdir>/<files>"
	print "\t\t\t\t * <subdir> : Ontologies/"
	print "\t\t\t\t * <subfiles> : *.obo\n"
	sys.exit(2) 
	
def main(argv):
	""" If run as main script, function executes. """
	topDir = ""
	try:
		opts, args = getopt.getopt(argv,"hp:",["help","dirPath="])
		if len(argv) == 0:
			howToRun()
	except getopt.GetoptError:
		howToRun()
	for opt, arg in opts:
		print opt, arg
		if opt == "-h":
			howToRun()
		elif opt in ("-p", "--dirPath"):
			if not arg.endswith("/"):
				arg = arg + "/"
			startTime = time.clock()
			topDir = arg
			locale.setlocale(locale.LC_ALL, "")
			outPath = createOutDirectory(topDir)
			uniqueNodeSet = set()
			relnSet = set()
			totalNodeCount = 0
			for root, dirs, files in os.walk(topDir):

				""" Ontologies """
				if root.endswith("Ontologies"):
					print "\n\n\n\t\t=====================================  PARSING Ontologies ====================================="
					print "\nProcessing files in:\n\n\t%s" %root
					for oboFile in files:
						if oboFile.endswith(".obo"):
							nodeSet = set()
							oboFilePath = os.path.join(root, oboFile)
							with open(oboFilePath, "r") as inFile:
								blockList = getBlock(inFile)
								termList, typedefList, metaData = sortBlocks(blockList)
							editedSource = editSource(getSource(metaData), oboFilePath)
							
							# write nodes and relationships from individual ontology files
							if not oboFilePath.endswith(("GOmfbp_to_ChEBI03092015.obo", "molecular_function_xp_chebi03092015.obo")):
								print "\n%s" %oboFilePath
								# creates OntologyParser object for each term block
								for term in termList:
									dataDict = parseTagValue(term)
									ontologyObj = OntologyParser(**dataDict)

									# Skips obsolete nodes
									if ontologyObj.skipObsolete() is True:
										continue

									# creates node strings
									nodeString = "%s|%s|%s|%s|%s|%s\n" %(ontologyObj.getID(), ontologyObj.getName(), editedSource, ontologyObj.getDef(), ontologyObj.getSynonyms(), ontologyObj.getLabel())
									nodeString = nodeString.replace("None", "").replace("|p|", "|plant_ontology|")
									nodeSet.add(nodeString)
									uniqueNodeSet.add(ontologyObj.getID())

									# creates relationship strings within ontology files, adds to relnSet
									for reln in ontologyObj.getRelationships():
										relnString = "%s|%s|%s|%s" %(reln[0], editedSource, reln[2], reln[1])
										relnSet.add(relnString)

								# writes nodes
								nodeOutFile = (topDir + "csv_out/" + editedSource + ".csv")
								nodeCount = writeNodes(nodeOutFile, nodeSet)
								totalNodeCount += nodeCount
								print "\t%s nodes have been created from this ontology." %locale.format("%d", nodeCount, True)

							# creates relationship strings for cross-ontology files, adds to relnSet
							else:
								relnCount = 0
								for term in termList:
									dataDict = parseTagValue(term)
									ontologyObj = OntologyParser(**dataDict)
									for reln in ontologyObj.getRelationships():
										relnString = "%s|%s|%s|%s" %(reln[0], editedSource, reln[2], reln[1])
										relnSet.add(relnString)
										relnCount += 1
								print "\n%s" %oboFilePath
								print "\t%s relationships have been created from this ontology." %locale.format("%d", relnCount, True)

			# write relationships
			relnOutFile = (topDir + "csv_out/oboRelnOut.csv")
			totalRelnCount = writeRelationships(relnOutFile, uniqueNodeSet, relnSet)
			
			endTime = time.clock()
			duration = endTime - startTime
			print "\n%s nodes and %s ontology relationships have been created." %(locale.format("%d", totalNodeCount, True), locale.format("%d", totalRelnCount, True))
			print "\nIt took %s seconds to create all ontology nodes and relationships. \n\n" %duration
			
if __name__ == "__main__":
	main(sys.argv[1:])