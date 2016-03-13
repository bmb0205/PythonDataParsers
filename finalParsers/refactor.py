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
import importlib
from sourceClasses import SourceClass


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
            sourceString = arg
    # startTime = time.clock()
    locale.setlocale(locale.LC_ALL, "")
    outDir = general.createOutDirectory(topDir)

    sourceList = sourceString.strip().split(',')

    #  Runs for each source
    for source in sourceList:
        print '\n~~~~~~~~~~~~~~~~~~~~~~\n', source
        jsonPath = os.path.join(topDir, 'jsonFiles', source.lower() + '.json')

        try:
            # extract nested JSON data structure, safe_load ensures non unicode strings
            with open(jsonPath, 'r') as jsonInfile:
                jsonDump = json.dumps(json.load(jsonInfile))
                jsonDict = yaml.safe_load(jsonDump)

                #  Prepare attribute args for each file and upcoming class creation
                for file, attributeList in jsonDict.iteritems():
                    filePath = os.path.join(topDir, source, file)
                    outPath = os.path.join(outDir, file + ".out")
                    fileHeader = [attr.replace('+', '').replace('$', '').replace(' ', '_') for attr in attributeList]
                    inputAttributes = [attr[1:] for attr in attributeList if '+' in attr or '$' in attr]
                    ignoredAttributes = [attr[1:] for attr in attributeList if '$' in attr]
                    outHeader = [attr for attr in inputAttributes if attr not in ignoredAttributes]

                    #  Differentiate sources here by importing sourceClasses.py module
                    #  and dynamically calling source classes
                    # print '\n'
                    # print file
                    classModule = importlib.import_module('sourceClasses')
                    MySourceClass = getattr(classModule, source)
                    # print outPath, '\n'
                    # print 'attributeList: ', attributeList, '\n'
                    # print 'fileHeader: ', fileHeader, '\n'
                    # print 'input Attributes: ', inputAttributes, '\n'
                    # print 'ignored: ', ignoredAttributes, '\n'
                    # print 'outHeader: ', outHeader, '\n'
                    sourceInstance = MySourceClass(file, source, outPath, filePath, outHeader, inputAttributes, fileHeader, ignoredAttributes)
                    sourceInstance.checkFile()

        except IOError:
            print "Could not properly load .json file."
            sys.exit()

if __name__ == "__main__":
    main(sys.argv[1:])
