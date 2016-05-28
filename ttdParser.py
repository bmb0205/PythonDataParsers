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


# class TTDParser(object):

#     def __init__(self, outPath, sourcePath, fileList):
#         self.sourcePath = sourcePath
#         self.fileList = fileList
#         self.outPath = outPath

#     def parseTTD(self):
#         """ Therapeutic Target Database """

#         print "\n\n\n============== PARSING THERAPEUTIC TARGET DATABASE (TTD) ==============="

#         startTime = time.clock()

#         # Create all outfiles, open them, and write header lines
#         ttdNodeOutFile = open((self.outPath + 'ttdNodeOut.csv'), 'w')
#         targetDiseaseNodeOutFile = open((self.outPath + 'ttdNodeOut2.csv'), 'w')
#         KEGGNodeOutFile = open((self.outPath + 'KEGGNodeOut.csv'), 'w')
#         KEGGRelnOutFile = open((self.outPath + 'targetKEGGRelnOut.csv'), 'w')
#         wikiNodeOutFile = open((self.outPath + 'wikiNodeOut.csv'), 'w')
#         wikiRelnOutFile = open((self.outPath + 'targetWikiRelnOut.csv'), 'w')
#         ttdNodeOutFile.write("Source_ID:ID|Name|Source|Function|Diseases|Synonyms:string[]|KEGG_Pathway|Wiki_Pathway|:LABEL\n")
#         targetDiseaseNodeOutFile.write("Source_ID:ID|Name|Source|Diseases:String[]|:LABEL\n")
#         KEGGNodeOutFile.write("Source_ID:ID|Name|Source|:LABEL\n")
#         KEGGRelnOutFile.write(":START_ID|Source|:END_ID|:TYPE\n")
#         wikiNodeOutFile.write("Source_ID:ID|Name|Source|:LABEL\n")
#         wikiRelnOutFile.write(":START_ID|Source|:END_ID|:TYPE\n")

#         print "\nProcessing files in:\n\t%s\n" % self.sourcePath

#         for ttdFile in self.fileList:

#             ttdFilePath = os.path.join(self.sourcePath, ttdFile)

#             if ttdFilePath.endswith("TTD_download_raw.txt"):
#                 print ttdFilePath
#                 nodeDict, nodeSet = parseTTDNodes(ttdFilePath)
#                 nodeCount = writeTTDNodes(nodeDict, ttdNodeOutFile)

#                 tempPath = self.sourcePath + "/target-disease_TTD2016.txt"
#                 print tempPath
#                 targetDict = parseTargetDisease(tempPath, nodeSet)
#                 nodeCount2 = writeTargetDiseaseNodes(targetDict, targetDiseaseNodeOutFile)

#             elif ttdFilePath.endswith("Target-KEGGpathway_all.txt"):
#                 print ttdFilePath
#                 KEGGRelnCount = parseTargetKEGG(ttdFilePath, KEGGNodeOutFile, KEGGRelnOutFile)

#             elif ttdFilePath.endswith("Target-wikipathway_all.txt"):
#                 print ttdFilePath
#                 wikiRelnCount = parseTargetWiki(ttdFilePath, wikiNodeOutFile, wikiRelnOutFile)

#         endTime = time.clock()
#         duration = endTime - startTime
#         print ("\n%s total Therapeutic Target Database nodes have been created." %
#                (locale.format('%d', (nodeCount + nodeCount2), True)))
#         print ("\n%s total Therapeutic Target Database relationships have been created." %
#                (locale.format('%d', (KEGGRelnCount + wikiRelnCount), True)))
#         print "\nIt took %s seconds to create all TTD nodes and relationships\n" % duration


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


def main(argv):
    """ If run as main script, function executes with user input """
    topDir = ""
    try:
        opts, args = getopt.getopt(argv, "hp:", ["help", "dirPath="])
        if len(argv) == 0:
            general.howToRun()
    except getopt.GetoptError:
        general.howToRun()
    for opt, arg in opts:
        if opt in ['-h', '--help']:
            general.howToRun()
        elif opt in ("-p", "--dirPath"):
            if not arg.endswith("/"):
                arg = arg + "/"

            topDir = arg
            locale.setlocale(locale.LC_ALL, "")
            outPath = general.createOutDirectory(topDir)
            sourceList = os.listdir(topDir)[::-1]

            for source in sourceList:
                sourcePath = os.path.join(topDir + source)
                fileList = os.listdir(sourcePath)

                """ Therapeutic Target Database """
                if sourcePath.endswith('TTD'):
                    ttd = TTDParser(outPath, sourcePath, fileList)
                    ttd.parseTTD()


if __name__ == "__main__":
    main(sys.argv[1:])
