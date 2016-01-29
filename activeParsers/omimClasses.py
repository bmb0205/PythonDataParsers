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
		self.title = columns[7].strip()
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

	def getPheneKey(self):
		if len(self.disorder_info) > 3:
			return self.disorder_info[-3:]

	def getDisorderInfo(self):
		if not self.disorder_info == "":
			return self.disorder_info

	def multiReplace(self, myDict, originalString):
		""" observed from Python Cookbook, 2nd edition """
		compiled = re.compile("|".join(map(re.escape, myDict)))
		def getMatch(match):
			return myDict[match.group(0)]
		return compiled.sub(getMatch, originalString)


	def getDisorderTextAndMIM(self):
		splitter = " \(\d\), "
		found_id = "\d{6}"
		if not self.disorder_info == "":
			found = re.search(splitter, self.disorder_info)
			if found: # multiple disorders
				disorders = re.split(splitter, self.disorder_info)
				joined_disorders = ";".join(disorders)
				clean_joined_disorders = joined_disorders[:-4]
				raw = re.findall(found_id, clean_joined_disorders)
				myDict = dict()
				if raw: # contain disorder MIMs
					for ID in raw:
						myDict[ID] = ("MIM:" + ID)
					return MIMNode.multiReplace(self, myDict, clean_joined_disorders)
				else: # do not contain disorder MIMs, gene id = disorder id, all have same MIM
					cleaned_info = self.disorder_info[:-4] + ", " + self.gene_id + "P"
					return cleaned_info
			else: # one disorder
				found = re.search(found_id, self.disorder_info)
				if found: # contain disorder MIMs
					cleaned_info = self.disorder_info.replace(found.group(0), ("MIM:" + found.group(0)) )[:-4]
					return cleaned_info
				else: # do not contain disorder MIM, gene id = disorder id
					# print self.disorder_info
					cleaned_info = self.disorder_info[:-4] + ", " + self.gene_id + "P"
					return cleaned_info

	def getDisorderMIM(self):
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

					if not ")" in split[-1]: # missing phene key in this one instance, uses empty string
						disorderMIM = "MIM:" + split[-1] + "p"
						pheneKey = ""
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
				relnSet.add((split[0], split[1], split[2]))
			else: # does not contain disorder MIMs
				relnSet.add((split[0], (self.gene_id + "p"), split[-1]))

		return relnSet







				# mySet.add((split[0], split[1], split[2]))
		# return mySet

			# joined_disorders = ";".join(disorders)
			# # print disorders, '\n', joined_disorders, '\n'
			# clean_joined_disorders = joined_disorders
			# raw = re.findall(found_id, clean_joined_disorders)

		# 	myDict = dict()
		# 	if raw: # contain disorder MIMs
		# 		for ID in raw:
		# 			myDict[ID] = ("MIM:" + ID)
		# 		return MIMNode.multiReplace(self, myDict, clean_joined_disorders)
		# 	else: # do not contain disorder MIMs, gene id = disorder id, all have same MIM
		# 		cleaned_info = self.gene_id + "P"
		# 		return cleaned_info
		# else: # one disorder
		# 	found = re.search(found_id, self.disorder_info)
		# 	if found: # contain disorder MIMs
		# 		cleaned_info = self.disorder_info.replace(found.group(0), ("MIM:" + found.group(0)) )[:-4]
		# 		return cleaned_info
		# 	else: # do not contain disorder MIM, gene id = disorder id
		# 		# print self.disorder_info
		# 		cleaned_info = self.gene_id + "P"
		# 		return cleaned_info

class MorbidMap(object):
	"""  """
	def __init__(self, columns):
		self.columns = columns
		self.disorder_info = columns[0].strip().replace("{", "").replace("}", "").replace("[", "").replace("]", "").replace("?", "").rsplit(" ",2)
		self.disorder_text = columns[0].strip().replace("{", "").replace("}", "").replace("[", "").replace("]", "").replace("?", "")
		self.gene_symbol = columns[1].strip()
		self.geneMIM = "MIM:" + columns[2].strip()
		self.cytogenetic_location = columns[3].strip()


	def getGeneSymbols(self):
		if "," in self.gene_symbol:
			symbols = self.gene_symbol.replace(", ", ";")
			return symbols
		else:
			if not self.gene_symbol == None:
				return self.gene_symbol
			else:
				return ""

	def getPheneKey(self):
		pheneKey = self.disorder_info[-1].rstrip(")").lstrip("(")
		if pheneKey == "1":
			return "Disorder placed by association. Underlying defect unknown."
		elif pheneKey == "2":
			return "Disorder placed by linkage. No mutation found."
		elif pheneKey == "3":
			return "Disorder has known molecular basis. Mutation found."
		else:
			return "Contiguous gene deletion or duplication syndrome. Multiple genes are deleted or duplicated."

	def getPheneMIM(self):
		pheneMIM = self.disorder_info[-2]
		m = "[A-Za-z]+"
		found = re.match(m, pheneMIM)
		if len(pheneMIM) < 3 or found: # no phene MIM, so gene MIM = phene MIM
			return (self.geneMIM + "P")
		else:
			return ("MIM:" + pheneMIM) # phene MIM present, gene MIM separae

	def getDisorderText(self):
		info = self.disorder_info[:-1]
		found_id = "\d{6}"
		match = re.search(found_id, info[-1])
		if match:
			return " ".join(info[:-1]).rstrip(",")
		else:
			return " ".join(info)


class MIMToGene(object):
	""" """
	def __init__(self, columns):
		self.columns = columns
		self.MIM_id = "MIM:" + columns[0].strip()
		self.type = columns[1].strip()
		self.gene_id = "ENTREZ:" + columns[2].strip()
		self.gene_symbol = columns[3].strip()

	def getGeneID(self):
		if not self.gene_id.endswith("-"):
			return self.gene_id
		else:
			return ""
