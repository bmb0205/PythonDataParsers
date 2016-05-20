#!/usr/bin/python

import sys
import os
import getopt
import time
import locale
import ttdParser
import meshParser
import general

"""
Need to write more here for docs. This script parses TTD and MeSH by importing meshParser.py
and ttdParser.py, and uses general methods from general.py
"""


def main(argv):
    """ If run as main script, function executes with user input """
    topDir = ""
    try:
        opts, args = getopt.getopt(argv, 'hp:', ['help', 'dirPath='])
        if len(argv) == 0:
            general.howToRun()
    except getopt.GetoptError:
        general.howToRun()
    for opt, arg in opts:
        if opt in ['-h', '--help']:
            general.howToRun()
        elif opt in ['-p', '--dirPath']:
            if not arg.endswith("/"):
                arg = arg + "/"
            topDir = arg
            locale.setlocale(locale.LC_ALL, "")
            outPath = general.createOutDirectory(topDir)

            """ Therapeutic Target Database (TTD) """
            ttdNodeOutFile = open((outPath + 'ttdNodeOut.csv'), 'w')
            targetDiseaseNodeOutFile = open((outPath + 'ttdNodeOut2.csv'), 'w')
            KEGGNodeOutFile = open((outPath + 'KEGGNodeOut.csv'), 'w')
            KEGGRelnOutFile = open((outPath + 'targetKEGGRelnOut.csv'), 'w')
            wikiNodeOutFile = open((outPath + 'wikiNodeOut.csv'), 'w')
            wikiRelnOutFile = open((outPath + 'targetWikiRelnOut.csv'), 'w')
            ttdNodeOutFile.write("Source_ID:ID|Name|Source|Function|Diseases|Synonyms:string[]|KEGG_Pathway|Wiki_Pathway|:LABEL\n")
            targetDiseaseNodeOutFile.write("Source_ID:ID|Name|Source|Diseases:String[]|:LABEL\n")
            KEGGNodeOutFile.write("Source_ID:ID|Name|Source|:LABEL\n")
            KEGGRelnOutFile.write(":START_ID|Source|:END_ID|:TYPE\n")
            wikiNodeOutFile.write("Source_ID:ID|Name|Source|:LABEL\n")
            wikiRelnOutFile.write(":START_ID|Source|:END_ID|:TYPE\n")

            """ Medical Subject Headings Database (MeSH) """
            meshNodeOutFile = open((outPath + 'meshNodeOut.csv'), 'w')
            meshRelnOutFile = open((outPath + 'meshRelnOut.csv'), 'w')
            meshNodeOutFile.write("Source_id:ID|Source|Term|Synonyms:string[]|Semantic_Type:string[]|Mesh_TreeNumber|:LABEL\n")
            meshRelnOutFile.write(":START_ID|source|:END_ID|Category|:TYPE\n")

            totalMeshNodeSet = set()

            sourceList = os.listdir(topDir)[::-1]

            for source in sourceList:
                sourcePath = os.path.join(topDir + source)
                fileList = os.listdir(sourcePath)

                """ Therapeutic Target Database """
                if sourcePath.endswith('TTD'):
                    startTime = time.clock()
                    print "\n\n\n================================ PARSING THERAPEUTIC TARGET DATABASE (TTD) ==================================="
                    print "\nProcessing files in:\n\t%s\n" % sourcePath
                    for ttdFile in fileList:
                        ttdFilePath = os.path.join(sourcePath, ttdFile)
                        if ttdFilePath.endswith("TTD_download_raw.txt"):
                            print ttdFilePath
                            nodeDict, nodeSet = ttdParser.parseTTDNodes(ttdFilePath)
                            nodeCount = ttdParser.writeTTDNodes(nodeDict, ttdNodeOutFile)

                            tempPath = sourcePath + "/target-disease_TTD2016.txt"
                            print tempPath
                            targetDict = ttdParser.parseTargetDisease(tempPath, nodeSet)
                            nodeCount2 = ttdParser.writeTargetDiseaseNodes(targetDict, targetDiseaseNodeOutFile)
                        elif ttdFilePath.endswith("Target-KEGGpathway_all.txt"):
                            print ttdFilePath
                            KEGGRelnCount = ttdParser.parseTargetKEGG(ttdFilePath, KEGGNodeOutFile, KEGGRelnOutFile)
                        elif ttdFilePath.endswith("Target-wikipathway_all.txt"):
                            print ttdFilePath
                            wikiRelnCount = ttdParser.parseTargetWiki(ttdFilePath, wikiNodeOutFile, wikiRelnOutFile)

                    endTime = time.clock()
                    duration = endTime - startTime
                    print ("\n%s total Therapeutic Target Database nodes have been created." %
                           (locale.format('%d', (nodeCount + nodeCount2), True)))
                    print ("\n%s total Therapeutic Target Database relationships have been created." %
                           (locale.format('%d', (KEGGRelnCount + wikiRelnCount), True)))
                    print "\nIt took %s seconds to create all TTD nodes and relationships\n" % duration

                """ Medical Subject Headings Database (MeSH) """
                if sourcePath.endswith('MeSH'):
                    startTime = time.clock()
                    print "\n\n\n================================ PARSING NLM MEDICAL SUBJECT HEADINGS (MeSH) DATABASE ================================"
                    print "\nProcessing files in:\n\t%s\n" % sourcePath
                    finalCount = 0
                    bigRelnDict = dict()
                    sortedFiles = sorted(fileList, key=len)
                    for meshFile in sortedFiles:
                        meshFilePath = os.path.join(sourcePath, meshFile)
                        print "%s" % meshFilePath
                        if not meshFilePath.endswith('mtrees2016.bin'):
                            treeRelnDict, fileNodeSet = meshParser.meshData(meshFilePath, meshNodeOutFile)
                            totalMeshNodeSet.update(fileNodeSet)
                            bigRelnDict.update(treeRelnDict)
                            finalCount += len(fileNodeSet)
                            print 'len(fileNodeSet): ', len(fileNodeSet)
                            print "\t%s nodes have been created from this file\n" % locale.format('%d', len(fileNodeSet), True)
                        else:
                            relnCount = meshParser.parseTree(meshFilePath, bigRelnDict, meshRelnOutFile)
                            print "\t%s relationships have been created from this file\n" % locale.format('%d', relnCount, True)

                    endTime = time.clock()
                    duration = endTime - startTime
                    print ("\n%s total NLM MeSH nodes and %s total relationships have been created..." %
                           (locale.format('%d', finalCount, True), locale.format('%d', relnCount, True)))
                    print "\nIt took %s seconds to create all NLM MeSH nodes and relationships \n" % duration


if __name__ == "__main__":
    main(sys.argv[1:])
