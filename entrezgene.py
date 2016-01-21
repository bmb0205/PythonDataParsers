#!/usr/bin/python

import re


		
##################################################################################################################
##########################################   MeSH   #########################################################
##################################################################################################################



class MeSHNode(object):
	""" """
	def __init__(self, **myDict):
		self.myDict = myDict

	def getKeys(self):
		return self.myDict.keys()

	def getValues(self):
		return self.myDict.values()


		
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
					cleaned_info = self.gene_id + "P"
					return cleaned_info
			else: # one disorder
				found = re.search(found_id, self.disorder_info)
				if found: # contain disorder MIMs
					cleaned_info = self.disorder_info.replace(found.group(0), ("MIM:" + found.group(0)) )[:-4]
					return cleaned_info
				else: # do not contain disorder MIM, gene id = disorder id
					# print self.disorder_info
					cleaned_info = self.gene_id + "P"
					return cleaned_info

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

##################################################################################################################
##########################################   Entrez Gene   #########################################################
##################################################################################################################

class GeneToGO(object):
	""" populates object with attributes from gene2go file for gene -> GO relationships """
	def __init__(self, columns):
		self.columns = columns
		self.tax_id = "NCBI_TAXONOMY:" + columns[0].strip()
		self.gene_id = "ENTREZ:" + columns[1].strip()
		self.go_id = columns[2].strip()
		self.go_term = columns[5].strip()
		self.predicate = columns[7].strip()

	def getPubmedID(self):
		""" returns pubmedID if not '-' """
		self.pubmed_id = self.columns[6].strip()
		if self.pubmed_id != "-" and self.pubmed_id != "None":
			return self.pubmed_id
		else:
			return ""

class GeneToTax(object):
	""" populates object with attributes from gene_group file for gene -> tax relationships """
	def __init__(self, columns):
		self.columns = columns
		self.tax_id = "NCBI_TAXONOMY:" + columns[0].strip()
		self.gene_id = "ENTREZ:" + columns[1].strip()
		self.predicate = columns[2].strip()
		self.other_tax_id = "NCBI_TAXONOMY:" + columns[3].strip()
		self.other_gene_id = "ENTREZ:" + columns[4].strip()


class GeneToMIM(object):
	""" populates object with attributes from mim2gene_medgen.txt file for gene -> MIM relationships """
	def __init__(self, columns):
		self.columns = columns
		self.MIM_id = "MIM:" + columns[0].strip()
		self.type = columns[2].strip()

	def getGeneID(self):
		self.gene_id = "ENTREZ:" + columns[1].strip()
		if not self.gene_id.endswith("-"):
			return self.gene_id
		else:
			return ""

	def getSource(self):
		self.source = self.columns[3].strip()
		if self.source != "-":
			return self.source
		else:
			return "ncbi_entrez_mim_to_gene"

	# def getSynonym(self):
	# 	self.synonym = self.columns[4].strip()
	# 	if self.synonym != "-":
	# 		return self.synonym
	# 	else:
	# 		return ""

class EntrezNode(object):
	""" populates object with attributes from .gene_info files for node creation """
	def __init__(self, columns):
		self.columns = columns
		self.tax_id = "NCBI_TAXONOMY:" + columns[0].strip()
		self.gene_id = "ENTREZ:" + columns[1].strip()
		self.symbol = columns[2].strip()
		self.preferred_term = columns[8].strip()

	def getSynonyms(self):
		""" returns synonym if not '-' """
		self.synonyms = self.columns[4].strip()
		if self.synonyms != "-":
			return self.synonyms
		else:
			return ""

	def getSymbolFromNom(self):
		""" returns synonym if not '-' """
		self.symbol_from_nom = self.columns[10].strip()
		if self.symbol_from_nom != "-":
			return self.symbol_from_nom
		else:
			return ""

	def getOtherDesignations(self):
		""" returns synonym if not '-'' """
		self.other_designations = self.columns[13].strip()
		if self.other_designations != "-":
			return self.other_designations
		else:
			return ""