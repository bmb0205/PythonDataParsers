#!/usr/bin/python

import sys
import os
import getopt
import time
import locale
from ttdParser import parseTargetKEGG

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
    cleaned = string.replace(';', ',')
    return cleaned


def howToRun():
    """
    Instructs users how to use script.
    opts/args: -h, help
    """
    print "\n\t\t * Run as: python /path/to/this/script.py -p /path/to/top/directory"
    print "\n\t\t * Example top directory: /Users/username/KnowledgeBase/Sources"
    print "\n\t\t * Top directory structure: \n\t\t\t * /Users/username/KnowledgeBase/Sources/<sourceDirectory>/<files>"
    print "\t\t\t\t * <sourceDirectory> : MeSH/"
    print "\t\t\t\t * <files> : *.bin\n"
    sys.exit()


def main(argv):
    """ If run as main script, function executes with user input """
    topDir = ""
    try:
        opts, args = getopt.getopt(argv, 'hp:', ['help', 'dirPath='])
        if len(argv) == 0:
            howToRun()
    except getopt.GetoptError:
        howToRun()
    for opt, arg in opts:
        if opt in ['-h', '--help']:
            howToRun()
        elif opt in ['-p', '--dirPath']:
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

            """ PARRRSEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE """

            sourceList = os.listdir(topDir)[::-1]

            for source in sourceList:
                sourcePath = os.path.join(topDir + source)
                fileList = os.listdir(sourcePath)


                """ Therapeutic Target Database """
                if sourcePath.endswith('TTD'):
                    print "\n\n\n================================ PARSING Therapeutic Target Database (TTD) ==================================="
                    print "\nProcessing files in:\n\t%s\n" % sourcePath
                    for ttdFile in fileList:
                        ttdFilePath = os.path.join(sourcePath, ttdFile)
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
                            KEGGRelnCount = ttdParser.parseTargetKEGG(ttdFilePath, KEGGNodeOutFile, KEGGRelnOutFile)
                        elif ttdFilePath.endswith("Target-wikipathway_all.txt"):
                            print ttdFilePath
                            wikiRelnCount = parseTargetWiki(ttdFilePath, wikiNodeOutFile, wikiRelnOutFile)




if __name__ == "__main__":
    main(sys.argv[1:])
