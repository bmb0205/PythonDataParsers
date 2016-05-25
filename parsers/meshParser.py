#!/usr/bin/python

import sys
import os
import getopt
import locale
import time
# import general
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
* Infile(s) [MeSH files, 2016 versions used]:
    * 2015 MeSH Descriptor (d2016.bin), https://www.nlm.nih.gov/mesh/download_mesh.html?
    * 2015 MeSH Qualifier (q2016.bin), https://www.nlm.nih.gov/mesh/download_mesh.html?
    * 2015 MeSH Supplementary Concept (c2016.bin), https://www.nlm.nih.gov/mesh/download_mesh.html?
    * 2015 MeSh Tree, (mtrees2016.bin) https://www.nlm.nih.gov/mesh/download_mesh.html?
* Outfile(s): meshNodeOut.csv, meshRelnOut.csv
"""

def meshData(meshFilePath, meshNodeOutFile):
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
    treeRelnDict = dict()
    fileNodeSet = set()

    with open(meshFilePath, 'rU') as meshFile:
        for block in getBlock(meshFile):  # generator object
            meshNodeDict = defaultdict(set)

            for attribute in block:
                split = attribute.split(' = ')
                if not len(split) == 1:
                    key = split[0]
                    value = split[1]
                    if key in ['MH', 'NM', 'SH']:
                        meshNodeDict['term'].add(value)
                    elif key == 'UI':
                        meshNodeDict['unique_id'].add(value)
                        fileNodeSet.add(value)
                    elif key in ['MH', 'RN', 'NM']:
                        meshNodeDict['synonyms'].add(value)
                    elif key == 'MN':
                        meshNodeDict['mesh_tree_number'].add(value)
                    elif key == 'ST':
                        meshNodeDict['semantic_type'].add(value)
                    elif key in ['ENTRY', 'PRINT ENTRY', 'SY']:
                        splitValue = value.split("|")
                        if len(splitValue) == 1:
                            meshNodeDict['synonyms'].add(splitValue[0])
                        else:
                            header = splitValue[-1]
                            meshNodeDict['synonyms'].add(splitValue[0])
                            headerIndex = header.index('d')
                            semanticRelationship = splitValue[headerIndex]
                            meshNodeDict['semantic_relationship'].add(semanticRelationship)
            uniqueID = "".join(meshNodeDict['unique_id'])
            treeNums = meshNodeDict['mesh_tree_number']
            if treeNums:
                for treeNum in treeNums:
                    treeRelnDict[treeNum] = uniqueID
            writeMeSHNodes(meshNodeDict, meshNodeOutFile)
    return treeRelnDict, fileNodeSet


def getBlock(meshFile):
    """ Yields generator object containing attributes for each new record  """
    block = list()
    for line in meshFile:
        if line.startswith("*NEWRECORD"):
            if block:
                yield block[1:-1]
            block = list()
        if line:
            block += [line.strip()]
    if block:
        yield block[1:-1]


def writeMeSHNodes(meshNodeDict, meshNodeOutFile):
    """
    Creates node string using properties from meshNodeDict.
    Writes nodes to meshNodeOutFile.
    """
    nodeString = ("%s|MeSH|%s|%s|%s|%s|Medical_Heading\n" %
                  (''.join(meshNodeDict['unique_id']), ''.join(meshNodeDict['term']),
                   ';'.join(meshNodeDict['synonyms']), ';'.join(meshNodeDict['semantic_type']),
                   ';'.join(meshNodeDict['mesh_tree_number'])))
    meshNodeOutFile.write(nodeString)


def parseTree(meshFilePath, bigRelnDict, meshRelnOutFile):
    """
    Parses MeSH Tree and creates a set of unique relationships.
    Uses bigRelnDict to map mesh tree numbers back to unique node IDs.
    Writes relationship from unique set.
    """
    uniqueRelnSet = set()
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
                            uniqueRelnSet.add(relnString1)
                            uniqueRelnSet.add(relnString2)
                    del splitNumbers[-1]
                    treeNumStart = treeNumEnd
    for reln in uniqueRelnSet:
        meshRelnOutFile.write(reln)
    return len(uniqueRelnSet)


def getType(typeLetter):
    """ Returns value (relationship type) for passed in typeLetter key """
    typeDict = {'A': 'Anatomy', 'B': 'Organisms', 'C': 'Diseases',
                'D': 'Chemicals_and_Drugs', 'E': 'Analytical_Diagnostic_and_Therapeutic_Techniques_and_Equipment',
                'F': 'Psychiatry_and_Psychology', 'G': 'Phenomena_and_Processes', 'H': 'Disciplines_and_Occupations',
                'I': 'Anthropology_Education_Sociology_and_Agriculture', 'J': 'Technology_Industry_Agriculture',
                'K': 'Humanities', 'L': 'Information_Science', 'M': 'Named_Groups', 'N': 'Health_Care',
                'V': 'Publication_Characteristics', 'Z': 'Geographical_Locations'}
    return typeDict[typeLetter]

##################################################################################################################
##########################################   General   #########################################################
##################################################################################################################


def clean(string):
    """ cleans lines of any characters that may affect neo4j database creation or import """
    cleaned = string.replace(";", ",")
    return cleaned
