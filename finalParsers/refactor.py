#!/usr/bin/python

import sys
import time
import getopt
import locale
import os
import general
import csv
from collections import defaultdict
# from ttdParser import TTDParser
# from meshParser import MeSHParser
# from ctdParser import CTDParser
import pprint
# from fileParser import FileParser
import json
import yaml
import codecs
from fileParsers import CsvFileParser


# def addHeaders(sourcePath, filePath):
#     """ """
#     headerList = list()
#     if sourcePath.endswith('CTD') or sourcePath.endswith('NCBIEntrezGene'):
#         headerList = csvHeader(filePath)
#     # elif sourcePath.endswith()
#     return headerList


# def csvHeader(filePath):
#     """ """
#     with open(filePath, 'rU') as inFile:
#         for line in inFile:
#             if line.startswith('#Format:'):
#                 tempHeader = line.strip().split(' (')[0]
#                 header = tempHeader.split(' ')[1:]
#                 return header
#             elif line.startswith('#MIM number'):
#                 header = line.lstrip('#').rstrip().split('\t')
#                 return header
#             elif line.startswith('# Fields:'):
#                 header = next(inFile)[2:].strip().split('\t')
#                 return header


def main(argv):
    """ If run as main script, function executes with user input """
    topDir = ""
    source = ""
    try:
        opts, args = getopt.getopt(argv, 'hp:s:', ['help', 'dirPath=', 'source='])
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
        elif opt in ['-s', '--source']:
            source = arg
    # startTime = time.clock()
    locale.setlocale(locale.LC_ALL, "")
    outDir = general.createOutDirectory(topDir)
    jsonPath = os.path.join(topDir, 'jsonFiles', source.lower() + '.json')

    try:
        with open(jsonPath, 'r') as jsonInfile:
            jsonDump = json.dumps(json.load(jsonInfile))
            jsonDict = yaml.safe_load(jsonDump)
            # pprint.pprint(jsonDict)


            #### Prepare attribute args for upcoming class

            for file, attributeList in jsonDict.iteritems():
                outPath = os.path.join(outDir, file + ".out")
                filePath = os.path.join(topDir, source, file)
                outHeaders = [attr[2:] for attr in attributeList if '++' in attr]
                fileHeader = [attr.replace('++', '').replace(' ', '_') for attr in attributeList]
               



                """
                okay so call classes from here, not from csv parser

                """

                #### Parse 
                #""" CsvFileParser class parsing NCBI Entrez Gene and CTD """
                print '\n', file
                if source in ['NCBIEntrezGene', 'CTD', 'Ensemble']:
                    csvInstance = CsvFileParser(file, source, outPath, filePath, outHeaders, fileHeader)
                    iterable = csvInstance.parseCsvFile()
                    print next(iterable)
                    # print next(iterable)
                    # print next(iterable)
                    # print next(iterable)
                    # print next(iterable)
                    continue
                    # for processedRow in csvInstance.parseCsvFile():
                    #     print processedRow



    except IOError:
        print "Could not properly load .json file."
        sys.exit()


if __name__ == "__main__":
    main(sys.argv[1:])


                    # if csvInstance.file.startswith("All"):  # no duplicate nodes
                        
                        # print csvInstance.outHeaders
                        # pprint.pprint(vars(csvInstance))

                        # nodeFileDict = defaultdict(lambda: defaultdict(set))
                        # print 'got here'


                        ## yes do this but zippedRow needs to be processed first in parser
                        ## update defaultdict while iterating...decide when to write
                        # for processedRow in csvInstance.parseCsv():



    # sourceList = os.listdir(topDir)[::-1]

    # structure = fileStructure(topDir, outDir, sourceList, outputHeaderList)

    
    # for source, structure in structure.iteritems():
    #     if source in ['CTD', 'NCBIEntrezGene']:
    #         print '\n\n', source
            # pprint.pprint(structure['fileList'])
            # obj = FileParser(source, structure, outputHeaderList)
            # for k, v in structure.iteritems():
            #     pprint.pprint(k)
            #     pprint.pprint(v)
            # for file in obj.fileList.keys():


        #         obj.filePath = os.path.join(obj.sourcePath, file)
        #         obj.file = file
        #         obj.writeRelationships()

            # """

            # working here
            # idea: make it so user can input source type as argument as well as string of desired attributes?
            # figure out how to differentiate between source types and make things more generic

            # need to specify which attributes needed from specific files
            # """













            # for source in sourceList:
            #   fileStructure(source)
            #     sourcePath = os.path.join(topDir + source)
            #     fileList = os.listdir(sourcePath)
            #     FileParser(outDir, sourcePath, file)

            #     # """ Therapeutic Target Database (TTD) """
            #     if sourcePath.endswith('TTD'):
            #         ttd = TTDParser(outDir, sourcePath, fileList)
            #         ttd.parseTTD()

            #     # """ Medical Subject Headings (MeSH) """
            #     elif sourcePath.endswith('MeSH'):
            #         mesh = MeSHParser(outDir, sourcePath, fileList)
            #         totalMeshNodeSet = mesh.parseMeSH()

            #         # """ Comparative Toxicogenomic Database (CTD) """
            #         sourcePath = os.path.join(topDir + "CTD/")
            #         fileList = os.listdir(sourcePath)
            #         ctd = CTDParser(outDir, sourcePath, fileList, totalMeshNodeSet)
            #         ctd.parseCTD()


# if __name__ == "__main__":
#     main(sys.argv[1:])
