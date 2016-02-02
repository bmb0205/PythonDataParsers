#!/usr/bin/python

import re

##################################################################################################################
##########################################   MIM   #########################################################
##################################################################################################################

class MIMNode(object):
	""" populates object with attributes from geneMap2.txt file for node creation """
	def __init__(self, columns):
		self.columns = columns
		self.cytogenetic_location = columns[4].strip()
		self.gene_symbol = columns[5].strip()
		self.name = columns[7].strip()
		self.gene_id = "MIM:" + columns[8].strip()
		self.disorder_info = columns[11].strip()

	def getGeneSymbols(self):
		if "," in self.gene_symbol:
			symbols = self.gene_symbol.replace(", ", ";")
			return symbols
		else:
			if not self.gene_symbol == None:
				return self.gene_symbol
			else:
				return ""

	def getDisorderInfo(self):
		splitter = "\(\d\); "
		found_id = "\d{6}"
		found = re.search(splitter, self.disorder_info)
		relnSet = set()
		if found: # multiple associated disorders
			disorders = re.split("; ", self.disorder_info)
			for dis in disorders:
				split = dis.rsplit(" ", 2)
				hasID = re.search(found_id, split[1])
				if not hasID: # missing disorder MIM, so gene MIM == disorder/phene MIM
					text = " ".join(split[:-1]).rstrip(",")
					if not ")" in split[-1]: # missing phene key in this one instance, due to OMIM error. Hardcode "(3)"
						disorderMIM = "MIM:" + split[-1] + "p"
						pheneKey = "(3)"
						relnSet.add((text, disorderMIM, pheneKey))
					else:
						disorderMIM = self.gene_id + "p"
						pheneKey = split[-1]
						relnSet.add((text, disorderMIM, pheneKey))
				else: # has disorder/phene MIM available
					relnSet.add((split[0].rstrip(","), "MIM:" + split[1], split[2]))
		else: # one disorder
			found = re.search(found_id, self.disorder_info)
			split = self.disorder_info.rsplit(" ", 2)
			if found: # contain disorder MIMs
				relnSet.add((split[0], ("MIM:" + split[1]), split[2]))
			else: # does not contain disorder MIMs
				relnSet.add(((split[0] + " " + split[1]), (self.gene_id + "p"), split[-1]))
		return relnSet


class MIMToGene(object):
	""" """
	def __init__(self, columns):
		self.columns = columns
		self.MIM_id = "MIM:" + columns[0].strip()
		self.type = columns[1].strip()
		self.gene_id = "ENTREZ:" + columns[2].strip()
