#!/usr/bin/python

import sys
import getopt
import os
import re
import time
import locale
import itertools
from ontologyClasses import OntologyParser

"""
##################################################################################################################
##########################################   Ontology Parser   #########################################################
##################################################################################################################

Written by: Brandon Burciaga

Parses files from multiple Ontologies for graph database node and relationship creation.
See howToRun() method for instructions.
Infile(s): CHEBI Ontology, Disease Ontology, Gene Ontology, Human Phenotype Ontology, Mammalian Phenotype Ontology, 
Molecular Function -> CHEBI Ontology, Plant Ontology, Plant Trait Ontology -  (*.dmp) files
Outfile(s): GOmfbp_to_ChEBI.csv, MPheno.ontology.csv, chebi_ontology.csv, disease_ontology.csv, gene_ontology.csv,
human_phenotype.csv, molecular_function_xp_chebi.csv, plant_trait_ontology.csv
Imports: ontologyClasses.py module

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
    if len(metaData) != 0:
        metaData = metaData[0]
        for line in metaData:
            header_stanza = line.split(": ",1)
            if header_stanza[0] == "default-namespace":
                source = header_stanza[1].strip()
                return source, None

def editSource(Source, oboFilePath):
    """ Edits source of data to more readable format """
    editedSource = ""
    if Source == None:
        if oboFilePath.endswith("GOmfbp_to_ChEBI03092015.obo"):
            editedSource = "GOtoCHEBI_ontology"
        else:
            editedSource = "molecular_function_xp_CHEBI_ontology"
    elif Source[1] is None:
        if Source[0].endswith("plant_ontology.obo"):
            editedSource = "plant_ontology"
        elif Source[0].endswith("MPheno.ontology"):
            editedSource = "mammalian_phenotype_ontology"
        else:
            editedSource = Source[0]
    return editedSource

def parseTagValue(block):
    """ Creates tag, value dictionary to set up parsing """
    data = dict()
    for item in block:
        if "(Spanish)" in item or "(Japanese)" in item or "!!!" in item:
            continue
        tag = item.split(": ")[0]
        value = item.split(": ", 1)[1]
        if not tag in data:
            data[tag] = []
        data[tag].append(value)
    return data

def writeNodes(nodeOutFile, nodeSet):
    """ Writes ontology nodes using attributes listed """
    nodeCount = 0
    with open(nodeOutFile, "w") as oboNodeOut:
        oboNodeOut.write("source_id:ID|name|source|def|synonyms:string[]|:LABEL\n")
        for node in nodeSet:
            node = clean(node)
            nodeCount += 1
            oboNodeOut.write(node)
    return nodeCount

def writeRelationships(relnOutFile, uniqueNodeSet, relnSet):
    """ Writes header and relationships to oboRelnOut.csv if the nodes exist """
    relnCount = 0
    count = 0
    badRelnOutFile = relnOutFile.rsplit("/", 1)[0] + "/badOntologyReln.csv"
    with open(relnOutFile, "w") as oboRelnOut, open(badRelnOutFile, "w") as badOntologyRelnOut:
        oboRelnOut.write(":START_ID|source|:END_ID|:TYPE\n")
        badOntologyRelnOut.write("# relationships with at least one missing node\n")
        for reln in relnSet:
            reln1 = reln.split("|")[0]
            reln2 = reln.split("|")[2]
            if reln1 in uniqueNodeSet and reln2 in uniqueNodeSet:
                relnCount += 1
                reln = clean(reln)
                oboRelnOut.write(reln + "\n")
            else: # skips relationships due to nodes not existing
                if reln1 not in uniqueNodeSet:
                    badOntologyRelnOut.write(reln + "\t\tMissing node:  " + reln1 + '\n')                    
                elif reln2 not in uniqueNodeSet:
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
    """ cleans lines of any characters that may affect neo4j database creation or import """
    cleaned = string.replace("'", "").replace('"', '')
    return cleaned

def howToRun():
    """ 
    Instructs users how to use script.
    opts/args: -h, help
    """
    print "\n\t\t * Run as: python /path/to/this/script.py -p /path/to/top/directory"
    print "\n\t\t * Example top directory: /Users/username/KnowledgeBasedDiscovery/"
    print "\n\t\t * Top directory structure: \n\t\t\t * /Users/username/KnowledgeBasedDiscovery/<subdir>/<files>"
    print "\t\t\t\t * <subdir> : Ontology/"
    print "\t\t\t\t * <subfiles> : *.dmp\n"
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

            nodeOutFile = (outPath + "oboNodeOut.csv")
            relnOutFile = (outPath + "oboRelnOut.csv")
            ontologyRoot = topDir + "Ontology/"
            
            print "\n\n\n\t\t\t\t=====================================  PARSING Ontologies ====================================="
            print "\n\t\t\t\t\t\t\t\t\tProcessing files in:\n\n\t\t\t\t\t\t\t\t%s\n" % ontologyRoot
            print "\n\t\t\t\t\t\t\t\t\t Files processed: \n"
            
            uniqueNodeSet = set()
            relnSet = set()
            totalNodeCount = 0
            for root, dirs, files in os.walk(topDir):
                if root.endswith("Ontology"):
                    for oboFile in files:

                        if oboFile.endswith(".obo"):
                            nodeSet = set()
                            oboFilePath = os.path.join(root, oboFile)

                            # get term, typedef and metadata lists from file
                            with open(oboFilePath, "r") as inFile:
                                blockList = getBlock(inFile)
                                termList, typedefList, metaData = sortBlocks(blockList)
                
                            Source = getSource(metaData)
                            editedSource = editSource(Source, oboFilePath)
                            
                            # write nodes and relationships from individual ontology files
                            if not oboFilePath.endswith(("GOmfbp_to_ChEBI03092015.obo", "molecular_function_xp_chebi03092015.obo")):

                                # create OntologyParser object for each term block
                                for term in termList:
                                    dataDict = parseTagValue(term)
                                    ontologyObj = OntologyParser(**dataDict)

                                    # Skips obsolete nodes
                                    if ontologyObj.skipObsolete() is True:
                                        continue

                                    # create node strings
                                    nodeString = "%s|%s|%s|%s|%s|%s\n" %(ontologyObj.getID(), ontologyObj.getName(), editedSource, ontologyObj.getDef(), ontologyObj.getSynonyms(), ontologyObj.getLabel())
                                    nodeString = nodeString.replace("None", "").replace("|p|", "|plant_ontology|")
                                    nodeSet.add(nodeString)
                                    uniqueNodeSet.add(ontologyObj.getID())

                                    # create relationship strings within ontology files, adds to relnSet
                                    for reln in ontologyObj.getRelationships():
                                        relnString = "%s|%s|%s|%s" %(reln[0], editedSource, reln[2], reln[1])
                                        relnSet.add(relnString)

                                # write nodes
                                nodeOutFile = (topDir + "csv_out/" + editedSource + ".csv")
                                nodeCount = writeNodes(nodeOutFile, nodeSet)
                                totalNodeCount += nodeCount
                                print "\t\t\t\t\t\t  %s " %oboFilePath
                                print "\t\t\t\t\t\t\t %s nodes have been created from this ontology.\n" %locale.format("%d", nodeCount, True)

                            # create relationship strings for cross-ontology files, adds to relnSet
                            else:
                                for term in termList:
                                    dataDict = parseTagValue(term)
                                    ontologyObj = OntologyParser(**dataDict)
                                    for reln in ontologyObj.getRelationships():
                                        relnString = "%s|%s|%s|%s" %(reln[0], editedSource, reln[2], reln[1])
                                        relnSet.add(relnString)

            # write relationships
            relnOutFile = (topDir + "csv_out/ontologyRelnOut.csv")
            relnCount = writeRelationships(relnOutFile, uniqueNodeSet, relnSet)
            
            endTime = time.clock()
            duration = endTime - startTime
            print "\n\t\t\t\t\t\t  %s nodes and %s ontology relationships have been created." %(locale.format("%d", totalNodeCount, True), locale.format("%d", relnCount, True))
            print "\n\t\t\t\t\t\tIt took %s seconds to create all ontology nodes and relationships. \n\n" %duration
            
if __name__ == "__main__":
    main(sys.argv[1:])