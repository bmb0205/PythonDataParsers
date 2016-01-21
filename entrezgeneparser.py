#!/usr/bin/python

import sys
import os
import getopt
import collections
import locale
import time
import re
from collections import defaultdict
from entrezgene import EntrezNode
from entrezgene import GeneToTax
from entrezgene import GeneToGO
from entrezgene import GeneToMIM
from entrezgene import MIMNode
from entrezgene import MorbidMap
from entrezgene import MIMToGene
from entrezgene import MeSHNode




"""
Main file parser used to parse and extract data from NCBI Entrez Gene, MeSH and OMIM databases.
Parsed information is written to pipe delimited .csv outfiles in a directory created by the script.
See howToRun() method below for help running script.
Written by: Brandon Burciaga
"""





##################################################################################################################
#########################################   NCBI Entrez Gene   ###########################################################
##################################################################################################################


def writeGeneNodes(geneFilePath, geneNodeOutFile, count):
	"""	writes NCBI entrez gene nodes to node outfile """
	geneSet = set()
	with open(geneFilePath, 'ru') as inFile:
		for line in inFile:
			print "\r\t\t\t\t\t\t\tCreating and writing nodes: %d" % (count),
			cleaned = clean(line)
			if cleaned.startswith("#"):
				continue
			count += 1
			columns = cleaned.split("\t")
			obj = EntrezNode(columns)
			if not obj.gene_id in geneSet:
				geneSet.add(obj.gene_id)
				synList = [obj.getSynonyms(), obj.getSymbolFromNom(), obj.getOtherDesignations(), obj.symbol]
				synList = filter(None, synList)
				synSet = addSynonyms(synList)
				synString = ";".join(synSet)
				node = "%s|ncbi_entrez_gene|%s|%s|Gene\n" %(obj.gene_id, obj.preferred_term, synString)
				geneNodeOutFile.write(node)
			else:
				print "lol", obj.gene_id
	print "\n\t\t\t\t\t\t%s nodes have been created from this file\n" %locale.format('%d', count, True)
	return geneSet, count


def addSynonyms(synList):
	"""	creates set of synonyms and excludes 'None' """
	synSet = set()
	for syn in synList:
		if syn != None:
			synSet.add(syn)
	return synSet

def getPredicate(obj):
	if obj.predicate == "Component":
		predicate = "is_a"
		return predicate
	elif obj.predicate == "Function":
		predicate = "performs"
		return predicate
	elif obj.predicate == "Process":
		predicate = "part_of"
		return predicate

def geneGOReln(geneFilePath, geneGORelnOutFile, combined):  # NCBIEntrezGene/gene2go.... geneSet is number of unique nodes written (2,007,027)
	""" creates relationships for entrez gene to GO and writes to outfile """
	with open(geneFilePath, 'ru') as inFile:
		geneGOMap = defaultdict(set)
		tempSet = set()
		for line in inFile:
			cleaned = clean(line) #.replace('"', "").replace("'", '').replace(";", ",")
			if cleaned.startswith("#"):
				continue
			columns = cleaned.strip().split("\t")
			obj = GeneToGO(columns)
			if obj.gene_id in combined: # check if the node exists and was written
				predicate = getPredicate(obj)

				myKey = "%s|ncbi_entrez_gene|%s|%s|%s\n" %(obj.gene_id, obj.go_id, obj.getPubmedID(), predicate)
				tempSet.add(myKey)
	count = 0
	for reln in tempSet:
		count += 1
		print "\r\t\t\t\tCreating and writing NCBI Entrez Gene -> Gene Ontology (GO) relationships: %d" % (count),
		geneGORelnOutFile.write(reln)
	print "tempSet len", len(tempSet)
	print "\n\t\t\t%s NCBI Entrez Gene -> Gene Ontology (GO) relationships have been created from this file\n" %locale.format('%d', len(tempSet), True)
	return len(tempSet)

def writeGeneGOReln(geneGOMap, geneGORelnOutFile):
	source = "ncbi_entrez_gene"
	count = 0
	for k, v in geneGOMap.iteritems():
		count += 1
		articles = ';'.join(v)
		reln = "%s|%s|%s|%s\n" %(k[0], source, k[2], k[1])
		geneGORelnOutFile.write(reln)
		print "\r\t\t\t\tCreating and writing NCBI Entrez Gene -> Gene Ontology (GO) relationships: %d" % (count),
	print "\n\t\t\t%s NCBI Entrez Gene -> Gene Ontology (GO) relationships have been created from this file\n" %locale.format('%d', count, True)


def geneTaxReln(geneFilePath, geneTaxRelnOutFile): # NCBIEntrezGene/gene_group
	""" creates relationships for entrez gene to NCBI taxonomy and writes to outfile """
	geneTaxMap = defaultdict(set)
	with open(geneFilePath, 'ru') as inFile:
		for line in inFile:
			cleaned = clean(line)
			if cleaned.startswith("#") or "sibling" in cleaned:
				continue
			mySet = set()
			columns = cleaned.strip().split("\t")
			obj = GeneToTax(columns)
			source = "ncbi_entrez_gene"
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
		source = "ncbi_entrez_gene"
		for alt_id in v:
			if "ENTREZ" in alt_id:
				altGeneList.append(alt_id)
			elif "TAXONOMY" in alt_id:
				altTaxList.append(alt_id)
		altGeneString = ';'.join(altGeneList)
		altTaxString = ';'.join(altTaxList)
		reln = "%s|%s|%s|%s|%s|%s\n" %(k[0], altTaxString, source, altGeneString, k[2], k[1])
		geneTaxRelnOutFile.write(reln)
		print "\r\t\t\t\t     Creating and writing NCBI Entrez Gene -> NCBI Taxonomy relationships: %d" % (count),
	print "\n\t\t\t\t%s NCBI Entrez Gene -> NCBI Taxonomy relationships have been created from this file\n" %locale.format('%d', count, True)


def geneMIMReln(geneFilePath): # NCBIEntrezGene/mim2gene_medgen.txt
	""" creates relationships for entrez gene to MIM and writes to outfile """
	geneMIMMap = defaultdict(set)
	relnSet = set()
	with open(geneFilePath, 'ru') as inFile:
		for line in inFile:
			cleaned = clean(line)
			if cleaned.startswith("#"):
				continue
			columns = cleaned.split("\t")
			obj = GeneToMIM(columns)
			if not obj.getGeneID() == "":
				myKey = (obj.getGeneID(), "ncbi_entrezGene", obj.MIM_id, "belongs_to")
				relnSet.add(myKey)
	return relnSet


def writeGeneMIMReln(combinedSet, geneMIMRelnOutFile):
	count = 0
	for reln in combinedSet:
		joined = "|".join(reln)
		joined = joined + "\n"
		geneMIMRelnOutFile.write(joined)
		count += 1
		print "\r\t\t\t\t\t     Creating and writing NCBI Entrez Gene -> MIM relationships: %d" % (count),
	print "\n\t\t\t\tAn additional %s NCBI Entrez Gene -> MIM relationships have been created from this file\n" %locale.format('%d', count, True)




##################################################################################################################
#########################################   MIM   ###########################################################
##################################################################################################################


# 4786 genes associated with disorders
def writeMIMgeneNodes(MIMFilePath, mimGeneNodeOutFile): # MIM/geneMap2.txt
	"""	writes MIM nodes to MIMOutFile """
	geneDisorderMap = dict()
	geneSet = set()
	with open(MIMFilePath, 'ru') as inFile:
		count = 0
		for line in inFile:
			columns = line.replace('"', "").replace("'", '').split("|")
			obj = MIMNode(columns)
			if not obj.disorder_info == "":
				found_id = "\d{6}"
				# print obj.getDisorderMIM()
				pheneSet = set(re.findall(found_id, obj.getDisorderMIM()))
				pheneList = re.findall(found_id, obj.getDisorderMIM())
				pheneTextList = re.findall(";", obj.getDisorderMIM())
				# print "len pheneList", len(pheneSet)
				# print "len phene text", (len(pheneTextList) + 1)
				# print obj.gene_id, pheneList

				# for phene in pheneList: # adds relns that map back to themselves due to missing pheneMIM
				# 	if obj.gene_id[3:] == phene:
				# 		geneSet.add((obj.gene_id, "OMIM", (phene+"P"), "associated_with"))

				# if len(pheneList) != (len(pheneTextList)+1):
				# 	diff = (len(pheneTextList)+1) - len(pheneList)



					# print obj.getDisorderMIM()
					# print diff, obj.gene_id, pheneList, '\n'


					# print len(pheneList), (len(pheneTextList)+1), obj.getDisorderMIM(), '\n'
				

				for phene in pheneSet:
					pheneID = ("MIM:" + phene)
					if not obj.gene_id == pheneID:
						geneSet.add((obj.gene_id, "OMIM", pheneID,  "associated_with"))
					else:
						geneSet.add((obj.gene_id, "OMIM", (pheneID+"P"),  "associated_with"))
				# geneDisorderMap[obj.gene_id] = obj.getDisorderInfo() # for relationships
			
			mimGeneNode = "%s|OMIM|%s|%s|%s|Gene\n" %(obj.gene_id, obj.getGeneSymbols(), obj.cytogenetic_location, obj.title)
			mimGeneNodeOutFile.write(mimGeneNode)
			count += 1
	return count, geneDisorderMap, geneSet

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


##################################################################################################################
##########################################   MeSH   #########################################################
##################################################################################################################


def parseMeSH(MeSHFilePath, count, meshNodeOutFile):
	"""
	Creates defaultdict of MeSH block attributes.
	Feeds dict and outfile into writeMeSHNodes() function
	"""
	with open(MeSHFilePath, 'ru') as meshFile:
		count = 0
		for block in getBlock(meshFile): # genrator object
			print "\r\t\t\t\t\t\t\t    Creating and writing nodes: %d" % (count),
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
						# print value
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
			writeMeSHNodes(myDict, meshNodeOutFile)
	return count

			# synonyms include: MH, ENTRY(take first field as synonym(a)...also take semantic relation(d), SY, NM, RN
			# mesh tree number MN for relationships, download MeSH tree

def getBlock(meshFile):
	""" method yields generator object for each new entry """
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
	keyList = ["unique_id", "term", "synonyms", "semantic_type", "mesh_tree_number"]
	for item in keyList:
		if not item in myDict.keys():
			myDict[item] = ''
	node = "%s|MeSH|%s|%s|%s|%s|MedicalHeading\n" %(";".join(myDict["unique_id"]), ";".join(myDict["term"]), ";".join(myDict["synonyms"]), ";".join(myDict["semantic_type"]), ";".join(myDict["mesh_tree_number"]))
	meshNodeOutFile.write(node)

# def writeMeSHRelationships


##################################################################################################################
##########################################   General   #########################################################
##################################################################################################################


def createOutDirectory(topDir):
	"""	creates path for out directory and outfiles """
	outPath = (str(topDir) + "csv_out/")
	if not os.path.exists(outPath):
		os.makedirs(outPath)
		print "\n\n\t\t\t\t\t\tOutfile directory path not found...\n\t\t\t\t\tOne created at %s\n" %outPath
	return outPath


def clean(string):
	"""	cleans lines of any characters that may affect neo4j database creation or import """
	cleaned = string.replace('"', "").replace("'", '').replace(";", ",").replace("|", ";")
	return cleaned


def howToRun():
	"""
	Instructs users how to use this module
	opt, args: -h, help
	"""
	print "\n\t\t *  Run as: python /path/to/this/script.py -p /path/to/top/directory"
	print "\n\t\t *  Example top directory: /Users/username/BiSD/KnowledgeBasedDiscovery/"
	print "\n\t\t *  Top directory structure: \n\t\t\t * /Users/username/BiSD/KnowledgeBasedDiscovery/<subdir>/<files>"
	print "\t\t\t\t *  <subdir> : NCBIEntrezGene, Ontology, Linguamatics, NCBITaxonomy, MIM"
	print "\t\t\t\t *  <subfiles> : *.gene2go, *.gene_group, *.gene_info\n\n"
	sys.exit(2) 


def main(argv):
	""" Does all the things """
	topDir = ''
	try:
		opts, args = getopt.getopt(argv,"hp:",["help","dirPath="])
		if len(argv) == 0:
			howToRun()
	except getopt.GetoptError:
		howToRun()
	for opt, arg in opts:
		if opt == '-h':
			howToRun()
		elif opt in ("-p", "--dirPath"):
			if not arg.endswith("/"):
				arg = arg + "/"
			topDir = arg
			locale.setlocale(locale.LC_ALL, "")

			outPath = createOutDirectory(topDir) # /Users/bburciag/BiSD/KnowledgeBasedDiscovery/csv_out
			
			# """ ENTREZ Gene """
			geneNodeOutFile = open((outPath + 'geneNodeOut.csv'), 'w')
			# geneTaxRelnOutFile = open((outPath + 'geneTaxRelnOut.csv'), 'w')
			# geneGORelnOutFile = open((outPath + 'geneGORelnOut.csv'), 'w')
			geneMIMRelnOutFile = open((outPath + 'geneMIMRelnOut.csv'), 'w')

			# geneNodeOutFile.write("source_id:ID|source|preferred_term|synonyms:string[]|:LABEL\n")
			# geneTaxRelnOutFile.write(":START_ID|alternate_tax_ids|source|alternate_gene_id|:END_ID|:TYPE\n")
			# geneGORelnOutFile.write(":START_ID|source|:END_ID|pubmed_articles:string[]|:TYPE\n")
			geneMIMRelnOutFile.write(":START_ID|source|:END_ID|:TYPE\n")

			# """ OMIM """
			# mimGeneNodeOutFile = open((outPath + 'mimGeneNodeOut.csv'), 'w')
			# mimDisorderNodeOutFile = open((outPath + 'mimDisorderNodeOut.csv'), 'w')
			# mimRelnOutFile = open((outPath + 'mimRelnOut.csv'), 'w')

			# mimGeneNodeOutFile.write("source_id:ID|source|gene_symbol:string[]|cytogenetic_location|title|:LABEL\n")
			# mimDisorderNodeOutFile.write("source_id:ID|source|disorder|status|:LABEL\n")
			# mimRelnOutFile.write(":START_ID|source|:END_ID|:TYPE\n")

			# """ MeSH """
			# meshNodeOutFile = open((outPath + 'meshNodeOut.csv'), 'w')
			# meshNodeOutFile.write("source_id:ID|source|term|synonyms:string[]|semantic_type:string[]|mesh_tree_number|:LABEL\n")


			for root, dirs, files in os.walk(topDir):

				# """ MESH """
				# if root.endswith("MeSH"):
				# 	print "\n\n\n\t\t================================ PARSING NLM MEDICAL SUBJECT HEADINGS (MeSH) DATABASE ================================"
				# 	print "\n\t\t\t\t\t\t\t\tProcessing files in:\n"
				# 	startTime = time.clock()
				# 	finalCount = 0
				# 	count = 0
				# 	for MeSHFile in files:
				# 		MeSHFilePath = os.path.join(root, MeSHFile)
				#  		print "    \t\t\t\t\t\t%s" %MeSHFilePath
				# 		count = parseMeSH(MeSHFilePath, count, meshNodeOutFile)
				# 		finalCount += count
				# 		print "\n\t\t\t\t\t\t\t%s nodes have been created from this file\n" %locale.format('%d', count, True)
				# 	endTime = time.clock()
				# 	duration = endTime - startTime
				# 	print "\n\t\t\t\t\t\t    %s total NLM MeSH nodes have been created..." %locale.format('%d', finalCount, True)
				# 	print "\n\t\t\t\t\t\t  It took %s seconds to create all NLM MeSH nodes" %duration

				# """ ONTOLOGY """
				# if root.endswith("Ontology"):
				# 	for ontologyFile in files:
				# 		ontologyFilePath = os.path.join(root, ontologyFile)
				# 		if ontologyFile.endswith()

				""" OMIM """
				if root.endswith("OMIM"):
					for MIMFile in files:

						MIMFilePath =  os.path.join(root, MIMFile)

				# 		if MIMFilePath.endswith("geneMap2.txt"):
				# 			count, geneDisorderMap, geneSet = writeMIMgeneNodes(MIMFilePath, mimGeneNodeOutFile)
				# 			# writeMIMRelationships(geneDisorderMap, mimRelnOutFile)
				# 		if MIMFilePath.endswith("morbidmap"):
				# 			count, geneSet = writeMIMdisorderNodes(MIMFilePath, mimDisorderNodeOutFile, geneDisorderMap, geneSet)
				# 			writeMIMRelationships(geneSet, mimRelnOutFile)
						if MIMFilePath.endswith("mim2gene.txt"):
							mimGeneRelnSet = MIMGeneReln(MIMFilePath, geneMIMRelnOutFile)


			# 	""" NCBI ENTREZ GENE """
				if root.endswith("NCBIEntrezGene"):
					count = 0
					print "\n\n\n\t\t\t================================ PARSING NCBI ENTREZ GENE DATABASE ==================================="
					print "\n\t\t\t\t\t\t\t\tProcessing files in:"
					nodeCountList = []
					nodeList = []
					bigSet = set()
					startTime = time.clock()
					for geneFile in files:
						geneFilePath = os.path.join(root, geneFile)
						if geneFilePath.endswith(".gene_info"):
							print "\n\t\t\t\t%s" %geneFilePath
							geneSet, geneNodeCount = writeGeneNodes(geneFilePath, geneNodeOutFile, count)
							print len(geneSet)
							nodeList.append(geneSet)
							nodeCountList.append(len(geneSet))
			# 			if geneFilePath.endswith("gene2go"):
			# 				set1 = nodeList[0]
			# 				set2 = nodeList[1]
			# 				combined = set1.union(set2)

			# 				print "\n\t\t\t\t\t%s" %geneFilePath
			# 				geneGORelnCount = geneGOReln(geneFilePath, geneGORelnOutFile, combined)
			# 			if geneFilePath.endswith("gene_group"):
			# 				print "\n\t\t\t\t\t%s" %geneFilePath
			# 				geneTaxRelnCount = geneTaxReln(geneFilePath, geneTaxRelnOutFile)
			# 			if geneFilePath.endswith("medgen.txt"):
			# 				geneMIMRelnSet = geneMIMReln(geneFilePath)
			# 		endTime = time.clock()
			# 		duration = endTime - startTime
			# 		print "\n\t\t\t\t\t   %s total NCBI Entrez Gene nodes have been created..." %locale.format('%d', (nodeCountList[0] + nodeCountList[1]), True)
			# 		print "\n\t\t\t   %s total NCBI Entrez Gene relationships have been created, excluding NCBI Entrez Gene -> MIM" %locale.format('%d', (geneGORelnCount + geneTaxRelnCount), True)

			# 		print "\n\t\t\t\t\tIt took %s seconds to create all NCBI Entrez nodes and relationships\n" %duration
				
			# print "\n\t\t\t\t\t Parsing NCBI Entrez Gene -> MIM files and creating unique set of relationships"
			# combinedSet = mimGeneRelnSet.union(geneMIMRelnSet)
			# writeGeneMIMReln(combinedSet, geneMIMRelnOutFile)


if __name__ == "__main__":
	main(sys.argv[1:])