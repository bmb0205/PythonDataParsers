#!/usr/bin/python

import sys
import time
import getopt
import locale
import os
from collections import defaultdict
from ctdClasses import ChemGeneIXNS


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


def ixnTypes(ctdFilePath):
    """ 
    ctdFilePath: /path/CTD_chem_gene_ixn_types.tsv
    Returns typeDict which maps meshID to code, description and parent code 
    """
    typeDict = defaultdict(lambda: defaultdict(str))
    with open(ctdFilePath, 'rU') as inFile:
        for line in inFile:
            if line.startswith('#'):
                continue
            columns = line.strip().split('\t')
            meshID = columns[0]
            typeDict[meshID]['code'] = columns[1]
            typeDict[meshID]['description'] = columns[2]
            try:
                typeDict[meshID]['parentCode'] = columns[3]
            except:
                typeDict[meshID]['parentCode'] = ''
    return typeDict


def parseCTD(tempCtdFilePath, totalMeshNodeSet, typeDict):
    """ 
    totalMeshNodeSet is set of all MeSH nodes
    """
    mySet = set()
    objDict = defaultdict(lambda: defaultdictionary(set))
    objList = list()
    # print 'totalMESHnodeset ', len(totalMeshNodeSet) # 259,978
    count = 0
    relnDict = defaultdict(lambda: defaultdict(set))
    with open(tempCtdFilePath, 'rU') as inFile:
        for line in inFile:
            if line.startswith('#'):
                continue
            columns = line.strip().split('\t')
            obj = ChemGeneIXNS(columns)
            objList.append(obj)
            # objDict[obj.meshID][]
    return objList


def writeRelnsAndMissingNodes(objList, totalMeshNodeSet):
    relnSet = set()
    Acount = 0
    newMeshNodeDict = defaultdict(lambda: defaultdict(set))
    for o in objList:

        # make new MeSH nodes if they aren't present from parsing MeSH files already
        if o.meshID not in totalMeshNodeSet:
            Acount += 1
            print vars(o)


        else:
            continue
    print Acount

            # for action in o.getInteractionActions():
            #     relnTup = (o.meshID, action, o.entrezGeneID)



            #     if relnTup in relnSet:
            #         continue
            #     else:
            #         relnString = '%s|Comparative_Toxicogenetics_Database|%s|%s'


        # print o.meshID
        # print o.entrezGeneID
        # print o.interaction
        # print o.getInteractionActions()
        # print '\n\n'








        #     relnTup = (obj.meshID, obj.entrezGeneID)
        #     if relnTup == ('C534883', '4149'):
        #         relnDict[relnTup]['interaction'].add(obj.interaction)
        #         relnDict[relnTup]['interactionAction'].update(obj.getInteractionActions())
        #         relnDict[relnTup]['type'].update(obj.getInteractionTypes())
        # for a, b in relnDict.iteritems():
        #     print a, b
            # relnDict[relnTup]['code']
            # relnDict[relnTup]['description']
            # relnDict[relnTup]['parentCode']
    # for k, v in relnDict.iteritems():
    #     print k, '\t', v, '\n\n'



            # relnSet.update(newObject.getInteractionActions())
    #         mySet.add(columns[1].strip())
    #         if columns[1].strip() not in totalMeshNodeSet:
    #             count += 1
    #             # print columns[1].strip()
    # print len(mySet), count

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


# def main(argv):
#     """ If run as main script, function executes with user input """
#     topDir = ""
#     try:
#         opts, args = getopt.getopt(argv, "hp:", ["help", "dirPath="])
#         if len(argv) == 0:
#             howToRun()
#     except getopt.GetoptError:
#         howToRun()
#     for opt, arg in opts:
#         if opt in ['-h', '--help']:
#             howToRun()
#         elif opt in ("-p", "--dirPath"):
#             if not arg.endswith("/"):
#                 arg = arg + "/"
#             startTime = time.clock()
#             topDir = arg
#             locale.setlocale(locale.LC_ALL, "")
#             outPath = createOutDirectory(topDir)

#             nodeOutFile = open((outPath + 'ttdNodeOut.csv'), 'w')

#             nodeOutFile.write("Source_ID:ID|Name|Source|Function|Diseases|Synonyms:string[]|KEGG_Pathway|Wiki_Pathway|:LABEL\n")

#             for root, dirs, files in os.walk(topDir):

#                 """ Comparative Toxicogenomics Database """
#                 if root.endswith("CTD"):
#                     print "\n\n\n================================ PARSING Comparative Toxicogenomics Database (CTD) ==================================="
#                     print "\nProcessing files in:\n"
#                     for ctdFile in files:
#                         ctdFilePath = os.path.join(root, ctdFile)
#                         if ctdFile == "CTD_chem_gene_ixns.tsv":
#                             parseCTD(ctdFilePath)


                    # endTime = time.clock()
                    # duration = endTime - startTime
                    # print ("\n%s total Therapeutic Target Database nodes have been created." %
                    #        (locale.format('%d', (nodeCount + nodeCount2), True)))
                    # print ("\n%s total Therapeutic Target Database relationships have been created." %
                    #        (locale.format('%d', (KEGGRelnCount + wikiRelnCount), True)))
                    # print "\nIt took %s seconds to create all TTD nodes and relationships\n" % duration

if __name__ == "__main__":
    main(sys.argv[1:])