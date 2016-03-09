#!/usr/bin/python

import sys
import time
import getopt
import locale
import csv
import os
import itertools
from collections import defaultdict
from ctdClasses import ChemGeneIXNS
from ctdClasses import ChemDisease
import general
from meshParser import MeSHParser



"""
Comparative Toxicogenomics Database (CTD) Parser

Written by: Brandon Burciaga

* Parses files from Comparative Toxicogenomics Database (CTD)
    for neo4j graph database node and relationship creation.
* Outfiles are .csv (pipe delimited) and generated with first line header of
    node IDs, attributes, types and labels for neo4j-import tool
* See general.howToRun() method for instructions using this script.
* Infile(s) [CTD files in .tsv format, 2015 versions used]:
    * CTD_chem_gene_ixns.tsv, http://ctdbase.org/
* Outfile(s):
"""


class CTDParser(object):
    """ """
    def __init__(self, outPath, sourcePath, fileList, totalMeshNodeSet):
        self.sourcePath = sourcePath
        self.fileList = fileList
        self.outPath = outPath
        self.totalMeshNodeSet = totalMeshNodeSet

    def parseCTD(self):
        """ Comparative Toxicogenomics Database (CTD) """

        print "\n\n\n================================ PARSING Comparative Toxicogenomics Database (CTD) ==================================="

        # startTime = clock.time()

        # ctdRelnOutFile = open((self.outPath + 'ctdRelnOut.csv'), 'w')
        # ctdRelnOutFile.write(":START_ID|Source|:END_ID|Interaction|Pubmed_ID|Type_Description|Type_Code|"
        #                      "Parent_Code|Studied_Organism|OrganismID|:TYPE\n")

        print "\nProcessing files in:\n"
        for ctdFile in self.fileList:
            ctdFilePath = os.path.join(self.sourcePath, ctdFile)
            outFile = os.path.join(self.outPath, ctdFile)
            writeRelationships(parser(ctdFilePath), outFile)




            # if ctdFile == "CTD_chem_gene_ixns.tsv":
            #     # typeDict = ixnTypes(ctdFilePath)
            #     tempCtdFilePath = self.sourcePath + "CTD_chem_gene_ixns.tsv"
            #     # objList = parseChemGene(tempCtdFilePath, self.totalMeshNodeSet)
            #     # writeChemGeneRelns(objList, typeDict, self.totalMeshNodeSet, ctdRelnOutFile)
            # elif ctdFile == "CTD_chemicals_diseases.tsv":
            #     writeRelationships(parser(ctdFilePath))
                # parseChemDisease(ctdFilePath)


def parser(ctdFilePath):
    csv.register_dialect('tabs', delimiter='\t')
    with open(ctdFilePath, 'rU') as inFile:
        for line in inFile:
            if line.startswith('# Fields:'):
                header = next(inFile)[2:].strip().split('\t')
                next(inFile)  # skip '#' line after header info
                break  # break for line loop now that header is obtained
        csvReader = csv.DictReader(inFile, dialect='tabs', fieldnames=header)
        for row in csvReader:
            yield row

# def myMap():
    # """


def writeRelationships(generator, outFile):
    """ """
    count = 0
    mySet = set()
    print outFile
    if outFile.endswith('chemicals_diseases.tsv'):
        for row in generator:
            print row['InferenceGeneSymbol']

    #     count += 1
    #     if (gen['ChemicalID'], gen['DiseaseID']) in mySet:
    #         print (gen['ChemicalID'], gen['DiseaseID']), gen['DiseaseName']
    #     else:
    #         mySet.add((gen['ChemicalID'], gen['DiseaseID']))
    # print count, len(mySet)



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
            typeName = columns[0]
            typeDict[typeName]['code'] = columns[1]
            typeDict[typeName]['description'] = columns[2]
            try:
                typeDict[typeName]['parentCode'] = columns[3]
            except:
                typeDict[typeName]['parentCode'] = ''
    return typeDict


def parseChemGene(tempCtdFilePath, totalMeshNodeSet):
    """
    totalMeshNodeSet is set of all MeSH nodes
    """
    objList = list()
    with open(tempCtdFilePath, 'rU') as inFile:
        for line in inFile:
            if line.startswith('#'):
                continue
            columns = line.strip().split('\t')
            obj = ChemGeneIXNS(columns)
            objList.append(obj)
    return objList


def writeChemGeneRelns(objList, typeDict, totalMeshNodeSet, ctdRelnOutFile):
    count = 0
    for o in objList:
        for action in o.getInteractionActions():
            typeName = action.split('_')[1]
            relnString = ("%s|Comparative_Toxicogenomics_Database|%s|%s|%s|%s|%s|%s|%s|%s|%s\n" %
                          (o.meshID, o.entrezGeneID, o.interaction, o.pubmedID, typeDict[typeName]['description'],
                           typeDict[typeName]['code'], typeDict[typeName]['parentCode'], o.getOrganism(),
                           o.getOrganismID(), action))
            ctdRelnOutFile.write(relnString)
            count += 1
    print "\t%s relationships have been created from this file\n" % locale.format('%d', count, True)


# def parseChemDisease(ctdFilePath):
    # """ """
    # csv.register_dialect('tabs', delimiter='\t')
    # with open(ctdFilePath, 'rU') as inFile:
    #     for line in inFile:
    #         if line.startswith('# Fields:'):
    #             header = next(inFile)[2:].strip().split('\t')
    #             next(inFile)  # skip '#' line after header info
    #             break  # break for line loop now that header is obtained
    #     csvReader = csv.DictReader(inFile, dialect='tabs', fieldnames=header)
    #     for row in csvReader:
    #         yield row


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
        elif opt in ["-p", "--dirPath"]:
            if not arg.endswith("/"):
                arg = arg + "/"
            topDir = arg
            locale.setlocale(locale.LC_ALL, "")
            outPath = general.createOutDirectory(topDir)
            sourceList = os.listdir(topDir)[::-1]

            for source in sourceList:
                sourcePath = os.path.join(topDir + source)
                fileList = os.listdir(sourcePath)

                # """ Medical Subject Headings (MeSH) """
                if sourcePath.endswith('MeSH'):
                    # mesh = MeSHParser(outPath, sourcePath, fileList)
                    # totalMeshNodeSet = mesh.parseMeSH()
                    totalMeshNodeSet = set()
                    # """ Comparative Toxicogenomic Database (CTD) """
                    sourcePath = os.path.join(topDir + 'CTD/')
                    fileList = os.listdir(sourcePath)
                    ctd = CTDParser(outPath, sourcePath, fileList, totalMeshNodeSet)
                    ctd.parseCTD()

if __name__ == "__main__":
    main(sys.argv[1:])