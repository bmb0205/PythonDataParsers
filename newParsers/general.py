#!/usr/bin/python

import sys
import os
from collections import OrderedDict
import yaml


"""
General
"""


# From Stack Overflow
# Answer: http://stackoverflow.com/a/21912744/4722282
# User: coldfix, http://stackoverflow.com/users/650222/coldfix
def ordered_load(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
    class OrderedLoader(Loader):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)


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
