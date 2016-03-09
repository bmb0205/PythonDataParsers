#!/usr/bin/python

import sys
import getopt
import os
import time
import locale
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
    * Disease Ontology, http://disease-ontologyorg/downloads/
    * Gene Ontology, http://geneontologyorg/page/download-ontology
    * Human Phenotype Ontology, http://human-phenotype-ontologygithub.io/downloads.html
    * Mammalian Phenotype Ontology, http://obofoundry.org/ontology/mp.html
    * Gene Ontology --> CHEBI Ontology, http://geneontologyorg/
    * Plant Ontoogy, Plant Trait Ontology, http://www.plantontologyorg/download
* Outfile(s): GOmfbp_to_ChEBI.csv, MPheno.ontologycsv, chebi_ontologycsv, disease_ontologycsv, gene_ontologycsv,
    human_phenotype.csv, molecular_function_xp_chebi.csv, plant_trait_ontologycsv
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
        print block, '\n'
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
            headerStanza = line.split(": ", 1)
            if headerStanza[0] == "default-namespace":
                source = headerStanza[1].strip()
                return source


def editSource(mySource, oboFilePath):
    """ Edits source of data to more readable format """
    editedSource = ""
    if mySource is None:
        if oboFilePath.endswith("GOmfbp_to_ChEBI03092015.obo"):
            editedSource = "Gene_Ontology"
        else:
            editedSource = "molecular_function_xp_CHEBI_ontology"
    else:
        if mySource.split('/')[-1] == "plant_ontology.obo":
            editedSource = "Plant_Ontology"
        elif mySource == "MPheno.ontology":
            editedSource = "Mammalian_Phenotype_Ontology"
        elif mySource == 'default_namespace':
            editedSource = "CTD_Exposure_Ontology"
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


def writeOntologyNodes(nodeOutFile, nodeSet):
    """ Writes ontology nodes using attributes listed """
    nodeCount = 0
    # print nodeOutFile
    with open(nodeOutFile, "w") as oboNodeOut:
        oboNodeOut.write("Source_ID:ID|Name|Source|Definition|Synonyms:string[]|:LABEL\n")
        for node in nodeSet:
            node = clean(node)
            nodeCount += 1
            oboNodeOut.write(node)
    return nodeCount


def writeOntologyRelationships(relnOutFile, bigUniqueNodeSet, bigRelnSet):
    """
    Writes header and relationships to oboRelnOut.csv if the nodes exist.
    """
    totalRelnCount = 0
    with open(relnOutFile, "w") as oboRelnOut:
        oboRelnOut.write(":START_ID|Source|:END_ID|:TYPE\n")
        for reln in bigRelnSet:
            startNode = reln.split("|")[0]
            endNode = reln.split("|")[2]
            if startNode in bigUniqueNodeSet and endNode in bigUniqueNodeSet:
                totalRelnCount += 1
                reln = clean(reln)
                oboRelnOut.write(reln + "\n")
    return totalRelnCount


def parseObo(topDir, oboFilePath, termList, editedSource):
    """
    Iterates terms in termList for the input .obo file, creates a dictionary of term information.
    Creates OntologyParser object with dictionary as input.
    Skips obsolete nodes, writes unique nodes to outfile, returns set of unique relationships.
    """
    uniqueNodeSet = set()
    nodeSet = set()
    relnSet = set()
    # creates OntologyParser object for each term block
    for term in termList:
        dataDict = parseTagValue(term)
        ontologyObj = OntologyParser(**dataDict)

        # Skips obsolete nodes
        if ontologyObj.skipObsolete() is True:
            continue

        # creates node strings
        nodeString = "%s|%s|%s|%s|%s|%s\n" % (ontologyObj.getID(), ontologyObj.getName(), editedSource, ontologyObj.getDef(), ontologyObj.getSynonyms(), ontologyObj.getLabel())
        nodeString = nodeString.replace("None", "").replace("|p|", "|plant_ontology|")
        nodeSet.add(nodeString)
        uniqueNodeSet.add(ontologyObj.getID())

        # creates relationship strings within ontology files, adds to relnSet
        for reln in ontologyObj.getRelationships():
            relnString = "%s|%s|%s|%s" % (reln[0], editedSource, reln[2], reln[1])
            relnSet.add(relnString)

    # writes nodes
    nodeOutFile = (topDir + "csv_out/" + editedSource + ".csv")
    nodeCount = writeOntologyNodes(nodeOutFile, nodeSet)
    print "\t%s nodes have been created from this ontology." % locale.format("%d", nodeCount, True)
    return uniqueNodeSet, relnSet, nodeCount


def parseRelnFiles(oboFilePath, termList, editedSource):
    """ """
    relnSet = set()
    for term in termList:
        dataDict = parseTagValue(term)
        ontologyObj = OntologyParser(**dataDict)
        for reln in ontologyObj.getRelationships():
            relnString = "%s|%s|%s|%s" % (reln[0], editedSource, reln[2], reln[1])
            relnSet.add(relnString)
    print "\t%s relationships have been created from this ontology\n" % locale.format("%d", len(relnSet), True)
    return relnSet


##################################################################################################################
##########################################   General   #########################################################
##################################################################################################################


def createOutDirectory(topDir):
    """ Creates path for out directory and outfiles """
    outPath = (str(topDir) + "csv_out/")
    if not os.path.exists(outPath):
        os.makedirs(outPath)
        print "\n\n\t\t\tOutfile directory path not found...\n\t\tOne created at %s\n" % outPath
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
    print "\n\t\t * Top directory structure: \n\t\t\t * /Users/username/KnowledgeBase/<subdir>/<files>"
    print "\t\t\t\t * <subdir> : Ontologies/"
    print "\t\t\t\t * <subfiles> : *.obo\n"
    sys.exit()


def main(argv):
    """ If run as main script, function executes with user input """
    topDir = ""
    try:
        opts, args = getopt.getopt(argv, "hp:", ["help", "dirPath="])
        if len(argv) == 0:
            howToRun()
    except getopt.GetoptError:
        howToRun()
    for opt, arg in opts:
        if opt in ['-h', '--help']:
            howToRun()
        elif opt in ("-p", "--dirPath"):
            if not arg.endswith("/"):
                arg = arg + "/"
            startTime = time.clock()
            topDir = arg
            locale.setlocale(locale.LC_ALL, "")

            """ PARRRSEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE """
            sourceList = os.listdir(topDir)[::-1]  # ['TTD', 'Ontologies', 'OMIM', 'NCBITaxonomy', 'NCBIEntrezGene', 'NAL', 'MeSH', 'CTD', 'csv_out']
            for source in sourceList:
                sourcePath = os.path.join(topDir + source)

                """ Ontologies """
                bigUniqueNodeSet = set()
                bigRelnSet = set()
                totalNodeCount = 0
                if sourcePath.endswith('Ontologies'):
                    print "\n\n\n=====================================  PARSING Ontologies ====================================="
                    print "\nProcessing files in:\n\t%s\n" % sourcePath
                    fileList = os.listdir(sourcePath)
                    for oboFile in fileList:
                        oboFilePath = os.path.join(sourcePath, oboFile)
                        with open(oboFilePath, "rU") as inFile:
                            blockList = getBlock(inFile)
                            termList, typedefList, metaData = sortBlocks(blockList)
                        editedSource = editSource(getSource(metaData), oboFilePath)

                        # write nodes and relationships from individual ontology files
                        if not oboFilePath.endswith(("GOmfbp_to_ChEBI03092015.obo", "molecular_function_xp_chebi03092015.obo")):
                            print "\n%s" % oboFilePath
                            uniqueNodeSet, relnSet, nodeCount = parseObo(topDir, oboFilePath, termList, editedSource)
                            totalNodeCount += nodeCount
                            bigRelnSet.update(relnSet)
                            bigUniqueNodeSet.update(uniqueNodeSet)

                        # creates relationship strings for cross-ontology files, adds to relnSet
                        else:
                            print "\n%s" % oboFilePath
                            relnSet = parseRelnFiles(oboFilePath, termList, editedSource)
                            bigRelnSet.update(relnSet)

                    # write relationships
                    relnOutFile = (topDir + "csv_out/oboRelnOut.csv")
                    totalRelnCount = writeOntologyRelationships(relnOutFile, bigUniqueNodeSet, bigRelnSet)

                    endTime = time.clock()
                    duration = endTime - startTime
                    print "\n%s nodes and %s ontology relationships have been created." % (locale.format("%d", totalNodeCount, True), locale.format("%d", totalRelnCount, True))
                    print "\nIt took %s seconds to create all ontology nodes and relationships. \n\n" % duration

if __name__ == "__main__":
    main(sys.argv[1:])