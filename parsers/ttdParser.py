#!/usr/bin/python

import sys
import time
import getopt
import locale
import os
# import general
from collections import defaultdict


"""
##################################################################################################################
##############################   Therapeutic Target Database (TTD) Parser   ####################################
##################################################################################################################

Written by: Brandon Burciaga

* Parses files from Therapeutic Target Database for neo4j graph database node and relationship creation.
* Outfiles are .csv (pipe delimited) and generated with first line header of
    node IDs, attributes, types and labels for neo4j-import tool
* See howToRun() method for instructions using this script.
* Infile(s) [TTD files in .txt format, 2015 versions used despite filename]:
    * TTD_download_raw.txt, http://database.idrb.cqu.edu.cn/TTD/TTD_Download.asp
    * Target-KEGGpathway_all.txt, http://database.idrb.cqu.edu.cn/TTD/TTD_Download.asp
    * Target-wikipathway_all.txt, http://database.idrb.cqu.edu.cn/TTD/TTD_Download.asp
    * target-disease_TTD2016.txt, http://database.idrb.cqu.edu.cn/TTD/TTD_Download.asp
* Outfile(s): ttdNodeOut.csv, ttdNodeOut2.csv, wikiNodeOut.csv, KEGGNodeOut.csv, targetKEGGRelnOut.csv, targetWikiRelnOut.csv
"""


def parseTTDNodes(ttdFilePath):
    """ Parses TTD_download_raw.txt for node information """
    # nodeDict: when accessing nodeDict[key][key_doesn't_exist], lambda: defaultdict(set) is called
    # and creates nodeDict[key][now_existing_key] = set(). Defaultdict(set) nested two levels.
    nodeDict = defaultdict(lambda: defaultdict(set))
    nodeSet = set()
    with open(ttdFilePath, 'rU') as inFile:
        for line in inFile:
            columns = line.strip().split('\t')
            if not len(columns) == 3:
                continue
            ttdID = columns[0]
            nodeSet.add(ttdID)
            nodeDict[ttdID][columns[1].replace(" ", "_")].add(columns[2])
    return nodeDict, nodeSet


def writeTTDNodes(nodeDict, nodeOutFile):
    """ Iterates nodeDict and writes nodes to outfile """
    for k, v in nodeDict.iteritems():
        nodeString = ('%s|%s|Therapeutic_Target_Database|%s|%s|%s|%s|%s|Protein_Target\n' %
                      (k, "; ".join(v['Name']), "; ".join(v['Function']).replace('|', ''),
                       "; ".join(v['Disease']), "; ".join(v['Synonyms']),
                       "; ".join(v['KEGG_Pathway']), "; ".join(v['Wiki_Pathway'])))
        nodeOutFile.write(nodeString)
    print "\t%s nodes have been created from this file.\n" % locale.format("%d", len(nodeDict), True)
    return len(nodeDict)


def parseTargetDisease(tempPath, nodeSet):
    """
    Parses target-disease_TTTD2016.txt for id, target name and indication.
    Adds above to targetDict
    """
    targetDict = defaultdict(lambda: defaultdict(set))
    with open(tempPath, 'rU') as inFile:
        for line in inFile:
            columns = line.strip().split("\t")
            if not len(columns) == 5:
                continue
            targetID = columns[0].strip()
            if targetID in nodeSet:
                continue
            targetDict[targetID]['Name'].add(columns[1].strip())
            targetDict[targetID]['Diseases'].add(columns[2].strip())
    return targetDict


def writeTargetDiseaseNodes(targetDict, targetDiseaseNodeOutFile):
    """ Iterates targetDict and writes more TTD nodes if they have not been created already by parseNodes """
    for k, v in targetDict.iteritems():
        nodeString = ("%s|%s|Therapeutic_Target_Database|%s|Protein_Target\n"
                      % (k, "".join(v['Name']), "; ".join(v['Diseases'])))
        targetDiseaseNodeOutFile.write(nodeString)
    print "\t%s nodes have been created from this file.\n" % locale.format("%d", len(targetDict), True)
    return len(targetDict)


def parseTargetKEGG(ttdFilePath, KEGGNodeOutFile, KEGGRelnOutFile):
    """ Creates and writes relationships from disease target 'TTDID' to KEGG pathway ID 'hsa' """
    KEGGCount = 0
    nodeSet = set()
    with open(ttdFilePath, 'rU') as inFile:
        for line in inFile:
            columns = line.strip().split("\t")
            if not len(columns) == 3 or columns[0] == "TTDID":
                continue
            KEGGNode = "%s|%s|KEGG|Pathway\n" % (columns[1], columns[2])
            nodeSet.add(KEGGNode)
            KEGGReln = "%s|Therapeutic_Target_Database|%s|part_of_pathway\n" % (columns[0], columns[1])
            KEGGReln2 = "%s|Therapeutic_Target_Database|%s|involves_protein\n" % (columns[1], columns[0])
            KEGGRelnOutFile.write(KEGGReln)
            KEGGRelnOutFile.write(KEGGReln2)
            KEGGCount += 2
    for node in nodeSet:
        KEGGNodeOutFile.write(node)
    print ("\t%s KEGG nodes and %s disease target --> KEGG relationships have been created from this file.\n" %
           (locale.format("%d", len(nodeSet), True), locale.format("%d", KEGGCount, True)))
    return KEGGCount


def parseTargetWiki(ttdFilePath, wikiNodeOutFile, wikiRelnOutFile):
    """
    Parses Target-wikipathway_all.txt.
    Creates and writes relationships from disease target TTDID to Wiki pathway ID WP.
    """
    wikiCount = 0
    nodeSet = set()
    with open(ttdFilePath, 'rU') as inFile:
        for line in inFile:
            columns = line.strip().split('\t')
            if not len(columns) == 3 or columns[0] == "TTDID":
                continue
            wikiCount += 2
            wikiNode = "%s|%s|Wiki|Pathway\n" % (columns[1], columns[2])
            nodeSet.add(wikiNode)
            wikiReln = "%s|Therapeutic_Target_Database|%s|part_of_pathway\n" % (columns[0], columns[1])
            wikiReln2 = "%s|Therapeutic_Target_Database|%s|involves_protein\n" % (columns[1], columns[0])
            wikiRelnOutFile.write(wikiReln)
            wikiRelnOutFile.write(wikiReln2)
    for node in nodeSet:
        wikiNodeOutFile.write(node)
    print ("\t%s Wiki Pathway nodes and %s disease target --> Wiki relationships have been created from this file.\n" %
           (locale.format("%d", len(nodeSet), True), locale.format("%d", wikiCount, True)))
    return wikiCount
