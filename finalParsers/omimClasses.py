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
		disorderMIM = ''
		if found: # multiple associated disorders
			disorders = re.split("; ", self.disorder_info)


			for dis in disorders:
				split = dis.rsplit(" ", 2)
				hasID = re.search(found_id, split[1])
				if not hasID: # missing disorder MIM, so gene MIM == disorder/phene MIM + 'p'



					# print 'lol', self.gene_id, '\t', self.disorder_info, '\n'
					# lol MIM:600020 	Neurofibrosarcoma (3); {Prostate cancer, susceptibility to}, 176807 (3) 

					# MIM:600020 	set([('Neurofibrosarcoma', 'MIM:600020p', '(3)'), ('{Prostate cancer, susceptibility to}', 'MIM:176807', '(3)')]) 
					# text = " ".join(split[:-1]).rstrip(",")
					
					disorderMIM = self.gene_id + "p"


					# print disorderMIM, self.columns, '\n'
					pheneKey = split[-1][1:-1]
					# print (self.gene_id, pheneKey, disorderMIM)
					# print split, '\n', self.columns, '\n\n' #self.disorder_info, '\n\n'
					relnSet.add((self.gene_id, pheneKey, disorderMIM))
				
				else: # has disorder/phene MIM available
					# print 'lol', self.gene_id, '\t', self.disorder_info, '\n'
					# text = split[0].rstrip(",")
					disorderMIM = "MIM:" + split[1]

					if self.gene_id == disorderMIM:
						print 'lolzzz', dis

					pheneKey = split[2][1:-1]
					# print (self.gene_id, pheneKey, disorderMIM)
					
					# print split, '\n', self.columns, '\n\n' #self.disorder_info, '\n\n'


					relnSet.add((self.gene_id, pheneKey, disorderMIM))
		

		else: # one disorder
			found = re.search(found_id, self.disorder_info)
			split = self.disorder_info.rsplit(" ", 2)
			if found: # contain disorder MIMs

				if not ")" in split[-1]: # missing phene key in this one instance, due to OMIM error. Hardcode "(3)"
					disorderMIM = "MIM:" + split[-1]
					relnSet.add((self.gene_id, "3", disorderMIM))
				else:
					disorderMIM = "MIM:" + split[1]
					pheneKey = split[2][1:-1]
					relnSet.add((self.gene_id, pheneKey, disorderMIM))
				# print 'lol', self.gene_id, '\t', self.disorder_info, '\n'
			else: # does not contain disorder MIMs
				# print 'lol', self.gene_id, '\t', self.disorder_info, '\n'
				# lol MIM:608687 	Spinocerebellar ataxia 20 (4) 

				# MIM:608687 	set([('Spinocerebellar ataxia 20', 'MIM:608687p', '(4)')]) 
				# print split, '\n', self.disorder_info, '\n\n'
				# text = " ".join(split[:2])
				disorderMIM = self.gene_id + 'p'
				pheneKey = split[-1][1:-1]
				relnSet.add((self.gene_id, pheneKey, disorderMIM))
			if self.gene_id == disorderMIM:
				print 'lol', self.disorder_info
		if self.gene_id == disorderMIM:
			print self.disorder_info
		return relnSet


class MIMToGene(object):
	""" """
	def __init__(self, columns):
		self.columns = columns
		self.MIM_id = "MIM:" + columns[0].strip()
		self.type = columns[1].strip()
		self.gene_id = "ENTREZ:" + columns[2].strip()

class DisorderNode(object):
	""" """
	def __init__(self, columns):
		self.columns = columns
		self.geneMIM = "MIM:" + columns[2].strip()
		self.disorderInfo = getDisorderNodeInfo(columns[0].strip(), self.geneMIM)
		self.text = self.disorderInfo[0].lstrip("{").lstrip("[").lstrip("?").rstrip(",").rstrip("}").rstrip("]")
		self.pheneKey = self.disorderInfo[-1][1:-1]
		self.disorderID = self.disorderInfo[1]


def getDisorderNodeInfo(disorder, geneMIM):
	""" Searches for disorder MIM for disorder MIM node. Uses gene MIM if not found. Returns tuple of text, MIM and phene key """
	found_id = "\d{6}"
	disorderInfo = ""
	found = re.search(found_id, disorder)
	split = disorder.rsplit(" ", 2)

	if found: # contain disorder MIMs
		if not ")" in split[-1]: # missing phene key in this one instance, due to OMIM error. Hardcode "(3)"
			disorderInfo = ((" ".join(split[:2])), ("MIM:" + split[-1]), "(3)") 
		else:
			disorderInfo = (split[0], ("MIM:" + split[1]), split[2])
	else: # does not contain disorder MIMs, use gene MIM + 'p'
		disorderInfo = ((split[0] + " " + split[1]), (geneMIM + "p"), split[-1])

	# print disorderInfo
	# print split, '\n', self.columns, '\n\n' #self.disorder_info, '\n\n'

	return disorderInfo