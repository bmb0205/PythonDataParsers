#!/usr/bin/python


from collections import defaultdict
import importlib


class NCBIEntrezGene(object):
    """
    Class for parsing All_Mammalia.gene_info, All_Plants.gene_info files
    Holds logic for processing NCBI Entrez Gene nodes in preparation for writing
    """
    def __init__(self, zippedRow, file):
        self.zippedRow = zippedRow
        self.file = file
        #  file checks here

    def processRow(self):
        """ Processes row depending on file """
        processedRow = defaultdict(str)

        processedRow['Gene_ID'] = ("ENTREZ:" + self.zippedRow['GeneID'])

        if self.file.endswith('gene_info'):

            synonymList = ['Symbol', 'Synonyms', 'Symbol_from_nomenclature_authority', 'Other_designations']
            processedRow['Synonym'] = ';'.join(self.zippedRow[x] for x in synonymList if self.zippedRow[x] != '-')
            processedRow['Preferred_Term'] = self.zippedRow['description']
            processedRow['Tax_ID'] = ("NCBI_TAXONOMY:" + self.zippedRow['tax_id'])
            return processedRow

        elif self.file == 'gene_group':
            if 'sibling' in self.zippedRow['relationship']:
                return None
            processedRow['Tax_ID'] = ("NCBI_TAXONOMY:" + self.zippedRow['tax_id'])
            processedRow['Relationship'] = self.zippedRow['relationship']
            processedRow['Other_Tax_ID'] = ("NCBI_TAXONOMY:" + self.zippedRow['Other_tax_id'])
            processedRow['Other_Gene_ID'] = ("ENTREZ_GENE:" + self.zippedRow['Other_GeneID'])
            return processedRow

        elif self.file == 'mim2gene_medgen':
            processedRow['MIM_ID'] = ("MIM:" + self.zippedRow['MIM_number'])
            processedRow['Source'] = self.zippedRow['Source'] if self.zippedRow['Source'] != '-' else 
            return processedRow

        elif self.file == 'gene2go':
            processedRow['Relationship'] = self.zippedRow['Category']
            processedRow['GO_ID'] = self.zippedRow['GO_ID'])
            return processedRow