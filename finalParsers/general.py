#!/usr/bin/python

import sys
import os

"""
General
"""


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
