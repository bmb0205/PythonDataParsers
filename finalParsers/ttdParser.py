#!/usr/bin/python

import sys
import time
import getopt
import locale
import os
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


def parseNodes(ttdFilePath):
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

            """ Therapeutic Target Database """
            nodeOutFile = open((outPath + 'ttdNodeOut.csv'), 'w')
            targetDiseaseNodeOutFile = open((outPath + 'ttdNodeOut2.csv'), 'w')
            KEGGNodeOutFile = open((outPath + 'KEGGNodeOut.csv'), 'w')
            KEGGRelnOutFile = open((outPath + 'targetKEGGRelnOut.csv'), 'w')
            wikiNodeOutFile = open((outPath + 'wikiNodeOut.csv'), 'w')
            wikiRelnOutFile = open((outPath + 'targetWikiRelnOut.csv'), 'w')

            nodeOutFile.write("Source_ID:ID|Name|Source|Function|Diseases|Synonyms:string[]|KEGG_Pathway|Wiki_Pathway|:LABEL\n")
            targetDiseaseNodeOutFile.write("Source_ID:ID|Name|Source|Diseases:String[]|:LABEL\n")
            KEGGNodeOutFile.write("Source_ID:ID|Name|Source|:LABEL\n")
            KEGGRelnOutFile.write(":START_ID|Source|:END_ID|:TYPE\n")
            wikiNodeOutFile.write("Source_ID:ID|Name|Source|:LABEL\n")
            wikiRelnOutFile.write(":START_ID|Source|:END_ID|:TYPE\n")

            for root, dirs, files in os.walk(topDir):

                """ Therapeutic Target Database """
                if root.endswith("TTD"):
                    print "\n\n\n================================ PARSING Therapeutic Target Database (TTD) ==================================="
                    print "\nProcessing files in:\n"
                    for ttdFile in files:
                        ttdFilePath = os.path.join(root, ttdFile)

                        if ttdFilePath.endswith("TTD_download_raw.txt"):
                            print ttdFilePath
                            nodeDict, nodeSet = parseNodes(ttdFilePath)
                            nodeCount = writeNodes(nodeDict, nodeOutFile)

                            tempPath = root + "/target-disease_TTD2016.txt"
                            print tempPath
                            targetDict = parseTargetDisease(tempPath, nodeSet)
                            nodeCount2 = writeTargetDiseaseNodes(targetDict, targetDiseaseNodeOutFile)
                        elif ttdFilePath.endswith("Target-KEGGpathway_all.txt"):
                            print ttdFilePath
                            KEGGRelnCount = parseTargetKEGG(ttdFilePath, KEGGNodeOutFile, KEGGRelnOutFile)
                        elif ttdFilePath.endswith("Target-wikipathway_all.txt"):
                            print ttdFilePath
                            wikiRelnCount = parseTargetWiki(ttdFilePath, wikiNodeOutFile, wikiRelnOutFile)

                    endTime = time.clock()
                    duration = endTime - startTime
                    print ("\n%s total Therapeutic Target Database nodes have been created." %
                           (locale.format('%d', (nodeCount + nodeCount2), True)))
                    print ("\n%s total Therapeutic Target Database relationships have been created." %
                           (locale.format('%d', (KEGGRelnCount + wikiRelnCount), True)))
                    print "\nIt took %s seconds to create all TTD nodes and relationships\n" % duration

if __name__ == "__main__":
    main(sys.argv[1:])
