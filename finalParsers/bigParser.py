#!/usr/bin/python

import sys
import os
import getopt
import time
import locale
import ttdParser
import meshParser
import ctdParser
import ontologyParser

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

            """ Comparative Toxicogenomics Database (CTD) """
            ctdRelnOutFile = open((outPath + 'ctdRelnOut.csv'), 'w')
            ctdRelnOutFile.write(":START_ID|Source|:END_ID|Interaction|Pubmed_ID|Type_Description|Type_Code|"
                                 "Parent_Code|Studied_Organism|OrganismID|:TYPE\n")

            totalMeshNodeSet = set()

            print os.listdir(topDir)
            sourceList = os.listdir(topDir)[::-1]
            print '\n\n', sourceList

            for source in sourceList:
                sourcePath = os.path.join(topDir + source)
                fileList = os.listdir(sourcePath)

                """ Therapeutic Target Database """
                if sourcePath.endswith('TTD'):
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

                    print ("\n%s total Therapeutic Target Database nodes have been created." %
                           (locale.format('%d', (nodeCount + nodeCount2), True)))
                    print ("\n%s total Therapeutic Target Database relationships have been created." %
                           (locale.format('%d', (KEGGRelnCount + wikiRelnCount), True)))
                    # print "\nIt took %s seconds to create all TTD nodes and relationships\n" % duration

######################
######################
######################
######################

                # if sourcePath.endswith('Ontologies'):
                #     """ Ontologies """
                #     bigUniqueNodeSet = set()
                #     bigRelnSet = set()
                #     totalNodeCount = 0
                #     if sourcePath.endswith('Ontologies'):
                #         print "\n\n\n=====================================  PARSING Ontologies ====================================="
                #         print "\nProcessing files in:\n\t%s\n" % sourcePath
                #         fileList = os.listdir(sourcePath)
                #         for oboFile in fileList:
                #             oboFilePath = os.path.join(sourcePath, oboFile)
                #             with open(oboFilePath, "rU") as inFile:
                #                 blockList = ontologyParser.getBlock(inFile)
                #                 termList, typedefList, metaData = ontologyParser.sortBlocks(blockList)
                #             editedSource = ontologyParser.editSource(ontologyParser.getSource(metaData), oboFilePath)

                #             # write nodes and relationships from individual ontology files
                #             if not oboFilePath.endswith(("GOmfbp_to_ChEBI03092015.obo", "molecular_function_xp_chebi03092015.obo")):
                #                 print "\n%s" % oboFilePath
                #                 uniqueNodeSet, relnSet, nodeCount = ontologyParser.parseObo(topDir, oboFilePath, termList, editedSource)
                #                 totalNodeCount += nodeCount
                #                 bigRelnSet.update(relnSet)
                #                 bigUniqueNodeSet.update(uniqueNodeSet)

                #             # creates relationship strings for cross-ontology files, adds to relnSet
                #             else:
                #                 print "\n%s" % oboFilePath
                #                 relnSet = ontologyParser.parseRelnFiles(oboFilePath, termList, editedSource)
                #                 bigRelnSet.update(relnSet)

                #         # write relationships
                #         relnOutFile = (topDir + "csv_out/oboRelnOut.csv")
                #         totalRelnCount = ontologyParser.writeOntologyRelationships(relnOutFile, bigUniqueNodeSet, bigRelnSet)

                #         # endTime = time.clock()
                #         # duration = endTime - startTime
                #         print "\n%s nodes and %s ontology relationships have been created." % (locale.format("%d", totalNodeCount, True), locale.format("%d", totalRelnCount, True))
                #         # print "\nIt took %s seconds to create all ontology nodes and relationships. \n\n" % duration

######################
######################
######################
######################

                """ Medical Subject Headings Database (MeSH) """
                if sourcePath.endswith('MeSH'):
                    print "\n\n\n================================ PARSING NLM MEDICAL SUBJECT HEADINGS (MeSH) DATABASE ================================"
                    print "\nProcessing files in:\n\t%s\n" % sourcePath
                    finalCount = 0
                    bigRelnDict = dict()
                    sortedFiles = sorted(fileList, key=len)
                    for meshFile in sortedFiles:
                        meshFilePath = os.path.join(sourcePath, meshFile)
                        print "%s" % meshFilePath
                        if not meshFilePath.endswith('mtrees2016.bin'):
                            treeRelnDict, fileNodeSet = meshParser.parseMeSH(meshFilePath, meshNodeOutFile)
                            totalMeshNodeSet.update(fileNodeSet)
                            bigRelnDict.update(treeRelnDict)
                            finalCount += len(fileNodeSet)
                            print 'len(fileNodeSet): ', len(fileNodeSet)
                            print "\t%s nodes have been created from this file\n" % locale.format('%d', len(fileNodeSet), True)
                        else:
                            relnCount = meshParser.parseTree(meshFilePath, bigRelnDict, meshRelnOutFile)
                            print "\t%s relationships have been created from this file\n" % locale.format('%d', relnCount, True)

                    # endTime = time.clock()
                    # duration = endTime - startTime
                    # print ("\n%s total NLM MeSH nodes and %s total relationships have been created..." %
                    #        (locale.format('%d', finalCount, True), locale.format('%d', relnCount, True)))
                    # print "\nIt took %s seconds to create all NLM MeSH nodes and relationships \n" % duration

                    """ Comparative Toxicogenomics Database """
                    newRoot = topDir + "CTD/"
                    if newRoot.endswith("CTD/"):
                        print "\n\n\n================================ PARSING COMPARATIVE TOXICOGENOMIC DATABASE (CTD) ==================================="
                        print "\nProcessing files in:\n\t%s\n" % newRoot
                        ctdFileList = os.listdir(newRoot)
                        for ctdFile in ctdFileList:
                            ctdFilePath = os.path.join(newRoot, ctdFile)
                            if ctdFile == "CTD_chem_gene_ixn_types.tsv":
                                typeDict = ctdParser.ixnTypes(ctdFilePath)
                                # tempCtdFilePath = newRoot + "CTD_chem_gene_ixns.tsv"
                                # objList = ctdParser.parseChemGene(tempCtdFilePath, totalMeshNodeSet)
                                # ctdParser.writeChemGeneRelns(objList, typeDict, totalMeshNodeSet, ctdRelnOutFile)
                            elif ctdFile == "CTD_chemicals_diseases.tsv":
                                ctdParser.parseChemDisease(ctdFilePath)

######################
######################
######################
######################



if __name__ == "__main__":
    main(sys.argv[1:])
