#!/usr/bin/python

import sys
import time
import getopt
import locale
import os
from collections import defaultdict


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

def parseCTD(ctdFilePath):
    """ """
    mySet = set()
    with open(ctdFilePath, 'rU') as inFile:
        for line in inFile:
            if line.startswith("#"):
                continue
            columns = line.strip().split('\t')
            mySet.add(columns[1].strip())
    print mySet, len(mySet)

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
    opts: -h, --help
    """
    print "\n\t\t * Run as: python /path/to/this/script.py -p /path/to/top/directory"
    print "\n\t\t * Example top directory: /Users/username/KnowledgeBase/"
    print "\n\t\t * Top directory structure: \n\t\t\t * /Users/username/KnowledgeBase/<subdir>/<files>"
    print "\t\t\t\t * <subdir> : CTD/"
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

            nodeOutFile = open((outPath + 'ttdNodeOut.csv'), 'w')

            nodeOutFile.write("Source_ID:ID|Name|Source|Function|Diseases|Synonyms:string[]|KEGG_Pathway|Wiki_Pathway|:LABEL\n")

            for root, dirs, files in os.walk(topDir):

                """ Comparative Toxicogenomics Database """
                if root.endswith("CTD"):
                    print "\n\n\n================================ PARSING Comparative Toxicogenomics Database (CTD) ==================================="
                    print "\nProcessing files in:\n"
                    for ctdFile in files:
                        ctdFilePath = os.path.join(root, ctdFile)
                        if ctdFile == "CTD_chem_gene_ixns.tsv":
                            parseCTD(ctdFilePath)


                    # endTime = time.clock()
                    # duration = endTime - startTime
                    # print ("\n%s total Therapeutic Target Database nodes have been created." %
                    #        (locale.format('%d', (nodeCount + nodeCount2), True)))
                    # print ("\n%s total Therapeutic Target Database relationships have been created." %
                    #        (locale.format('%d', (KEGGRelnCount + wikiRelnCount), True)))
                    # print "\nIt took %s seconds to create all TTD nodes and relationships\n" % duration

if __name__ == "__main__":
    main(sys.argv[1:])