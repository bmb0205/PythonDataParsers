#!/usr/bin/python

"""
##################################################################################################################
##########################################   Entrez Gene   #########################################################
##################################################################################################################

Module imported by entrezGeneParser.py for various ontology node and relationship creation.
Holds classes EntrezNode, GeneToGO, GeneToTax, GeneToMIM

"""



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
		pubmed_id = self.columns[6].strip()
		if pubmed_id != "-" and pubmed_id != "None":
			fixed_id = pubmed_id.replace("|", ";")
			return fixed_id
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
		gene_id = "ENTREZ:" + self.columns[1].strip()
		if not gene_id.endswith("-"):
			return gene_id
		else:
			return ""

	def getSource(self):
		source = self.columns[3].strip()
		if source != "-":
			return source
		else:
			return "NCBI_Entrez_Gene_to_OMIM"

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
		synonyms = self.columns[4].strip()
		if synonyms != "-":
			return synonyms
		else:
			return ""

	def getSymbolFromNom(self):
		""" returns synonym if not '-' """
		symbol_from_nom = self.columns[10].strip()
		if symbol_from_nom != "-":
			return symbol_from_nom
		else:
			return ""

	def getOtherDesignations(self):
		""" returns synonym if not '-'' """
		other_designations = self.columns[13].strip()
		if other_designations != "-":
			return other_designations
		else:
			return ""