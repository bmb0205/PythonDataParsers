#!/usr/bin/python

import sys
import time
import getopt
import locale
import os
import general
import csv
from collections import defaultdict
from ttdParser import TTDParser
from meshParser import MeSHParser
from ctdParser import CTDParser
import pprint
from fileParser import FileParser


def fileStructure(topDir, outPath, sourceList):
    """ """
    fileDict = defaultdict(lambda: defaultdict(dict))
    for source in sourceList:
        if source == 'csv_out':
            continue
        sourcePath = os.path.join(topDir, source)
        fileDict[source]['sourcePath'] = sourcePath
        fileDict[source]['outPath'] = outPath
        for file in os.listdir(sourcePath):
            filePath = os.path.join(sourcePath, file)
            fileDict[source]['fileList'][file] = addHeaders(sourcePath, filePath)
    return fileDict


def addHeaders(sourcePath, filePath):
    """ """
    headerList = list()
    if sourcePath.endswith('CTD') or sourcePath.endswith('NCBIEntrezGene'):
        headerList = csvHeader(filePath)
    # elif sourcePath.endswith()
    return headerList


def csvHeader(filePath):
    """ """
    with open(filePath, 'rU') as inFile:
        for line in inFile:
            if line.startswith('#Format:'):
                tempHeader = line.strip().split(' (')[0]
                header = tempHeader.split(' ')[1:]
                return header
            elif line.startswith('#MIM number'):
                header = line.lstrip('#').rstrip().split('\t')
                return header
            elif line.startswith('# Fields:'):
                header = next(inFile)[2:].strip().split('\t')
                return header


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
            # startTime = time.clock()
            topDir = arg
            locale.setlocale(locale.LC_ALL, "")
            outPath = general.createOutDirectory(topDir)

            sourceList = os.listdir(topDir)[::-1]

            structure = fileStructure(topDir, outPath, sourceList)

            for source, structure in structure.iteritems():

                obj = FileParser(source, structure)

                for file in obj.fileList.keys():

                    obj.filePath = os.path.join(obj.sourcePath, file)
                    obj.file = file
                    obj.writeRelationships()

                """

                working here
                idea: make it so user can input source type as argument as well as string of desired attributes?
                figure out how to differentiate between source types and make things more generic


                """

            # for source in sourceList:
            #   fileStructure(source)
            #     sourcePath = os.path.join(topDir + source)
            #     fileList = os.listdir(sourcePath)
            #     FileParser(outPath, sourcePath, file)

            #     # """ Therapeutic Target Database (TTD) """
            #     if sourcePath.endswith('TTD'):
            #         ttd = TTDParser(outPath, sourcePath, fileList)
            #         ttd.parseTTD()

            #     # """ Medical Subject Headings (MeSH) """
            #     elif sourcePath.endswith('MeSH'):
            #         mesh = MeSHParser(outPath, sourcePath, fileList)
            #         totalMeshNodeSet = mesh.parseMeSH()

            #         # """ Comparative Toxicogenomic Database (CTD) """
            #         sourcePath = os.path.join(topDir + "CTD/")
            #         fileList = os.listdir(sourcePath)
            #         ctd = CTDParser(outPath, sourcePath, fileList, totalMeshNodeSet)
            #         ctd.parseCTD()


if __name__ == "__main__":
    main(sys.argv[1:])
