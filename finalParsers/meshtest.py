#!/usr/bin/python

import sys
import os
from meshParser import parseMeSH


def parse2015(mesh2015):
    totalMeshNodeSet2015 = set()
    for file in os.listdir(mesh2015):
        meshFilePath = os.path.join(mesh2015 + '/' + file)
        print "%s" % meshFilePath
        if not meshFilePath.endswith('mtrees2015.bin'):
            nodeSet2015 = parseMeSH(meshFilePath) #, fileNodeCount, meshNodeOutFile)
            totalMeshNodeSet2015.update(nodeSet2015)
            # bigRelnDict.update(treeRelnDict)
            # finalCount += fileNodeCount
            # print "\t%s nodes have been created from this file\n" % locale.format('%d', fileNodeCount, True)
    return totalMeshNodeSet2015


def parse2016(mesh2015):
    totalMeshNodeSet2016 = set()
    for file in os.listdir(mesh2015):
        meshFilePath = os.path.join(mesh2015 + '/' + file)
        print "%s" % meshFilePath
        if not meshFilePath.endswith('mtrees2015.bin'):
            nodeSet2016 = parseMeSH(meshFilePath)  #, fileNodeCount, meshNodeOutFile)
            totalMeshNodeSet2016.update(nodeSet2016)
            # bigRelnDict.update(treeRelnDict)
            # finalCount += fileNodeCount
            # print "\t%s nodes have been created from this file\n" % locale.format('%d', fileNodeCount, True)
    return totalMeshNodeSet2016


def main(argv):
    mesh2015 = sys.argv[1]
    mesh2016 = sys.argv[2]
    totalMeshNodeSet2015 = parse2015(mesh2015)
    totalMeshNodeSet2016 = parse2016(mesh2016)

    print len(totalMeshNodeSet2015), '\n\n'
    print len(totalMeshNodeSet2016), '\n\n'
    print len(totalMeshNodeSet2016) - len(totalMeshNodeSet2015)

    missingSet = set()
    count = 0
    for i in totalMeshNodeSet2016:
        if i not in totalMeshNodeSet2015:
            count += 1
            missingSet.add(i)
    print '\n', len(missingSet), count, '\n\n\n'



    missingSet2 = set()
    count2 = 0
    for i in totalMeshNodeSet2015:
        if i not in totalMeshNodeSet2016:
            count2 += 1
            missingSet2.add(i)
    print '\n', len(missingSet2), count2, missingSet

    """

    1978 more nodes in 2016 set

    223 nodes in 2015 that are not in 2016


    2201 nodes in 2016 that are not in 2015
    """ 
    
if __name__ == "__main__":
    main(sys.argv[1:])
