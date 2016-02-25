#!/usr/bin/python

import sys
import os
import getopt
import locale
import time
from collections import defaultdict

"""
##################################################################################################################
################################   Medical Subject Headings (MeSH) Parser  ###############################################
##################################################################################################################

Written by: Brandon Burciaga

* Parses Medical Subject Heading (MeSH) database files for neo4j graph database
    node and relationship creation.
* Outfiles are .csv (pipe delimited) and generated with first line header demonstrating
    the format of the rest of the file (in columns)
* See howToRun() method for instructions using this script.
* Infile(s) [MeSH files, 2015 versions used]:
    * 2015 MeSH Descriptor (d2015.bin), https://www.nlm.nih.gov/mesh/download_mesh.html?
    * 2015 MeSH Qualifier (q2015.bin), https://www.nlm.nih.gov/mesh/download_mesh.html?
    * 2015 MeSH Supplementary Concept (c2015.bin), https://www.nlm.nih.gov/mesh/download_mesh.html?
    * 2015 MeSh Tree, (mtrees2015.bin) https://www.nlm.nih.gov/mesh/download_mesh.html?
* Outfile(s): meshNodeOut.csv, meshRelnOut.csv
"""


def parseMeSH(meshFilePath, count, meshNodeOutFile):
    """
    Creates defaultdict of MeSH block attributes.
    Feeds dict and outfile into writeMeSHNodes() function.

    Attributes:
    MH, NM, SH = MeSH Heading, Name of substance, Subheading (preferred term)
    MN = MeSH tree Number for relationship mapping
    UI = Unique Identifier
    RN = CAS Registry/EC Number
    ST = Semantic Type
    ENTRY, PRINT ENTRY, SY = Synonyms
    """
    relnDict = dict()
    count = 0
    nodeSet = set()
    with open(meshFilePath, 'ru') as meshFile:
        for block in getBlock(meshFile):  # genrator object
            count += 1
            block = block[1:-1]
            myDict = defaultdict(set)
            for attribute in block:
                split = attribute.split(" = ")
                if not len(split) == 1:
                    key = split[0]
                    value = split[1]
                    if key in ['MH', 'NM', 'SH']:
                        myDict["term"].add(value)
                    elif key == "UI":
                        myDict["unique_id"].add(value)
                        nodeSet.add(value)
                    elif key in ['MH', 'RN', 'NM']:
                        myDict["synonyms"].add(value)
                    elif key == "MN":
                        myDict["mesh_tree_number"].add(value)
                    elif key == "ST":
                        myDict["semantic_type"].add(value)
                    elif key in ['ENTRY', 'PRINT ENTRY', 'SY']:
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
            if treeNums:
                for tree in treeNums:
                    relnDict[tree] = unique
            writeMeSHNodes(myDict, meshNodeOutFile)
    return count, relnDict, nodeSet


def getBlock(meshFile):
    """ Yields generator object for each new entry """
    block = []
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
    """
    Checks myDict for keys in keyList, if not there, sets default to empty string.
    Writes nodes to meshNodeOutFile
    """
    keyList = ["unique_id", "term", "synonyms", "semantic_type", "mesh_tree_number"]
    for item in keyList:
        if item not in myDict.keys():
            myDict[item] = ""
    node = ("%s|MeSH|%s|%s|%s|%s|Medical_Heading\n" %
            (";".join(myDict["unique_id"]), ";".join(myDict["term"]),
             ";".join(myDict["synonyms"]), ";".join(myDict["semantic_type"]),
             ";".join(myDict["mesh_tree_number"])))
    meshNodeOutFile.write(node)


def parseTree(meshFilePath, bigRelnDict, meshRelnOutFile):
    """
    Parses MeSH Tree and creates a set of unique relationships.
    Uses bigRelnDict to map mesh tree numbers back to unique node IDs.
    Writes relationship from unique set.
    """
    uniqueSet = set()
    with open(meshFilePath, 'rU') as inFile:
        for line in inFile:
            heading, treeNumStart = line.strip().split(';')
            if not len(treeNumStart) == 3:
                splitNumbers = treeNumStart.split('.')
                while len(splitNumbers) > 1:
                    treeNumEnd = treeNumStart[:-4]
                    typeLetter = treeNumStart[0]
                    relnType = getType(typeLetter)
                    for i in range(len(splitNumbers)):
                        node1 = ".".join(splitNumbers[0:i])
                        if node1:
                            relnString1 = ("%s|MeSH|%s|%s|contains\n" %
                                           (bigRelnDict[node1], bigRelnDict[treeNumStart], relnType))
                            relnString2 = ("%s|MeSH|%s|%s|is_a_part_of\n" %
                                           (bigRelnDict[treeNumStart], bigRelnDict[node1], relnType))
                            uniqueSet.add(relnString1)
                            uniqueSet.add(relnString2)
                    del splitNumbers[-1]
                    treeNumStart = treeNumEnd
    count = 0
    for item in uniqueSet:
        count += 1
        meshRelnOutFile.write(item)
    return count


def getType(typeLetter):
    """ Returns value (relationship type) for passed in typeLetter key """
    typeDict = {'A': 'Anatomy', 'B': 'Organisms', 'C': 'Diseases',
                'D': 'Chemicals_and_Drugs', 'E': 'Analytical_Diagnostic_and_Therapeutic_Techniques_and_Equipment',
                'F': 'Psychiatry_and_Psychology', 'G': 'Phenomena_and_Processes', 'H': 'Disciplines_and_Occupations',
                'I': 'Anthropology_Education_Sociology_and_Agriculture', 'J': 'Technology_Industry_Agriculture',
                'K': 'Humanities', 'L': 'Information_Science', 'M': 'Named_Groups', 'N': 'Health_Care',
                'V': 'Publication_Characteristics', 'Z': 'Geographical_Locations'}
    return typeDict[typeLetter]

"""
##################################################################################################################
##############################   Comparative Toxicogenomics Database (CTD) Parser   ####################################
##################################################################################################################

Written by: Brandon Burciaga

* Parses files from Comparative Toxicogenomics Database (CTD)
    for neo4j graph database node and relationship creation.
* Outfiles are .csv (pipe delimited) and generated with first line header of
    node IDs, attributes, types and labels for neo4j-import tool
* See howToRun() method for instructions using this script.
* Infile(s) [CTD files in .tsv format, 2015 versions used]:
    * CTD_chem_gene_ixns.tsv, http://ctdbase.org/
* Outfile(s):
"""

def parseCTD(ctdFilePath, bigNodeSet):
    """ """
    mySet = set()
    print 'bignodeset ', len(bigNodeSet)
    count = 0
    with open(ctdFilePath, 'rU') as inFile:
        for line in inFile:
            if line.startswith("#"):
                continue
            columns = line.strip().split('\t')
            mySet.add(columns[1].strip())
            if columns[1].strip() not in bigNodeSet:
                count += 1
                # print columns[1].strip()
    print len(mySet), count


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
    """ cleans lines of any characters that may affect neo4j database creation or import """
    cleaned = string.replace(";", ",")
    return cleaned


def howToRun():
    """
    Instructs users how to use script.
    opts/args: -h, help
    """
    print "\n\t\t * Run as: python /path/to/this/script.py -p /path/to/top/directory"
    print "\n\t\t * Example top directory: /Users/username/KnowledgeBase/"
    print "\n\t\t * Top directory structure: \n\t\t\t * /Users/username/KnowledgeBase/<subdir>/<files>"
    print "\t\t\t\t * <subdir> : MeSH/"
    print "\t\t\t\t * <subfiles> : *.bin\n"
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
            outPath = createOutDirectory(topDir)

            meshNodeOutFile = open((outPath + 'meshNodeOut.csv'), 'w')
            meshRelnOutFile = open((outPath + 'meshRelnOut.csv'), 'w')
            meshNodeOutFile.write("source_id:ID|source|term|synonyms:string[]|semantic_type:string[]|mesh_tree_number|:LABEL\n")
            meshRelnOutFile.write(":START_ID|source|:END_ID|Category|:TYPE\n")
            bigNodeSet = set()
            for root, dirs, files in os.walk(topDir):

                """ MESH """
                if root.endswith("MeSH"):
                    print "\n\n\n\t\t================================ PARSING NLM MEDICAL SUBJECT HEADINGS (MeSH) DATABASE ================================"
                    print "\nProcessing files in:\n"
                    startTime = time.clock()
                    finalCount = 0
                    count = 0
                    bigRelnDict = dict()
                    sortedFiles = sorted(files, key=len)
                    for meshFile in sortedFiles:
                        meshFilePath = os.path.join(root, meshFile)
                        print "%s" % meshFilePath
                        if not meshFilePath.endswith("mtrees2015.bin"):
                            count, relnDict, nodeSet = parseMeSH(meshFilePath, count, meshNodeOutFile)
                            bigNodeSet.update(nodeSet)
                            bigRelnDict.update(relnDict)
                            finalCount += count
                            print "\t%s nodes have been created from this file\n" % locale.format('%d', count, True)
                        else:
                            relnCount = parseTree(meshFilePath, bigRelnDict, meshRelnOutFile)
                            print "\t%s relationships have been created from this file\n" % locale.format('%d', relnCount, True)

                    endTime = time.clock()
                    duration = endTime - startTime
                    print ("\n%s total NLM MeSH nodes and %s total relationships have been created..." %
                           (locale.format('%d', finalCount, True), locale.format('%d', relnCount, True)))
                    print "\nIt took %s seconds to create all NLM MeSH nodes and relationships \n" % duration

                    """ Comparative Toxicogenomics Database """
                    newRoot = topDir + "CTD/"
                    if root.endswith("CTD"):
                        print "\n\n\n================================ PARSING Comparative Toxicogenomics Database (CTD) ==================================="
                        print "\nProcessing files in:\n"
                        for ctdFile in files:
                            ctdFilePath = os.path.join(root, ctdFile)
                            if ctdFile == "CTD_chem_gene_ixns.tsv":
                                parseCTD(ctdFilePath, bigNodeSet)



            print len(bigNodeSet)

if __name__ == "__main__":
    main(sys.argv[1:])