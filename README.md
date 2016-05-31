# Biological Database Parsers

This directory contains python scripts that parse various scientific databases for use on a work related project. 

All scripts written by Brandon Burciaga. 

# Database sources


## NCBI Entrez Gene and Comparative Toxicogenomics Database (CTD)

* refractor.py
	* main module to run for CTD and NCBI Entrez Gene parsing
	* Run as: python refactor.py -p ~/path/to/top/dir -s source
		* source : 'CTD', 'NCBIEntrezGene'

	* Infile(s): 
		* User edited JSON data file specifying files and attributes to parse for each source
		* NCBI Entrez Gene data (ftp://ftp.ncbi.nih.gov/gene/DATA/)
		* Comparative Toxicogenomics Database (http://ctdbase.org/)
	* Outfile(s):
		* Pipe delimited files in the directory created through createOutDirectory() function in general.py
		* View specific source parsers for specifics on outfiles

* ncbientrezgene.py
	* Holds logic for processing NCBI Entrez Gene nodes and relationships in preparation for writing to outfiles

* ctd.py
	* Class is work in progress
	* Holds logic for processing Comparative Toxicogenomics Database nodes and relationships in preparation for writing to outfiles

* parent.py
	* SourceClass is the parent class for each specific source class (NCBIEntrezGene, CTD)
    * Contains attributes passed in from main() function in refactor.py, and
    * Class methods shared between the child classes for header fixing and generic tsv parsing

* general.py
	* Contains general functions for creating output directory, running help flags, etc used by parent.py and refractor.py

## NCBI Taxonomy 

* taxonomyParser.py
	* Parses NCBI Taxonomy database files for neo4j graph database node and relationship creation.
	* Outfiles are .csv (pipe delimited) and generated with first line header demonstrating the format of the rest of the file (in columns)
	* See howToRun() method for instructions using this script.
	* Infile(s) [NCBI Taxonomy files in .dmp format, 2015 versions used]:
	    * nodes.dmp, ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/
	    * names.dmp, ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/
	    * citations.dmp, ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/
	* Outfile(s): taxNodeOut.csv, taxRelnOut.csv
	* Imports: taxonomyClasses.py

## Therapeutic Target Database (TTD), Medical Subject Headings (MeSH)

* ttdMeshParser.py is used to call the below modules
	* see general.py or -h to find out how to use this script

* ttdParser.py
	* Parses files from Therapeutic Target Database for neo4j graph database node and relationship creation.
	* Outfiles are .csv (pipe delimited) and generated with first line header of
	    node IDs, attributes, types and labels for neo4j-import tool
	* Infile(s) [TTD files in .txt format, 2015 versions used despite filename]:
	    * TTD_download_raw.txt, http://database.idrb.cqu.edu.cn/TTD/TTD_Download.asp
	    * Target-KEGGpathway_all.txt, http://database.idrb.cqu.edu.cn/TTD/TTD_Download.asp
	    * Target-wikipathway_all.txt, http://database.idrb.cqu.edu.cn/TTD/TTD_Download.asp
	    * target-disease_TTD2016.txt, http://database.idrb.cqu.edu.cn/TTD/TTD_Download.asp
	* Outfile(s): ttdNodeOut.csv, ttdNodeOut2.csv, wikiNodeOut.csv, KEGGNodeOut.csv, targetKEGGRelnOut.csv, targetWikiRelnOut.csv


* meshParser.py
	* Parses Medical Subject Heading (MeSH) database files for neo4j graph database
	    node and relationship creation.
	* Outfiles are .csv (pipe delimited) and generated with first line header demonstrating
	    the format of the rest of the file (in columns)
	* Infile(s) [MeSH files, 2015 versions used]:
	    * 2015 MeSH Descriptor (d2015.bin), https://www.nlm.nih.gov/mesh/download_mesh.html?
	    * 2015 MeSH Qualifier (q2015.bin), https://www.nlm.nih.gov/mesh/download_mesh.html?
	    * 2015 MeSH Supplementary Concept (c2015.bin), https://www.nlm.nih.gov/mesh/download_mesh.html?
	    * 2015 MeSh Tree, (mtrees2015.bin) https://www.nlm.nih.gov/mesh/download_mesh.html?
	* Outfile(s): meshNodeOut.csv, meshRelnOut.csv


## National Agricultural Library (NAL)

* nalParser.py
	* Parses National Agricultural Library thesaurus for neo4j graph database
    	node and relationship creation.
	* Outfiles are .csv (pipe delimited) and generated with first line header demonstrating
    	the format of the rest of the file (in columns)
	* See howToRun() method for instructions using this script.
	* Infile(s) [NAL Thesaurus, 2015 versions used]:
	    * NAL_Thesaurus_2015.xml, http://agclass.nal.usda.gov/download.shtml
	* Outfile(s): nalNodeOut.csv


## Online Mendelian Inheritance in Man (OMIM)

* omimParser.py
	* Parses Online Mendelian Inheritance in Man (OMIM) database files
    	for neo4j graph database node and relationship creation.
	* Outfiles are .csv (pipe delimited) and generated with first line header demonstrating
	   	the format of the rest of the file (in columns)
	* See howToRun() method for instructions using this script.
	* Infile(s) [OMIM files, 2015 versions used]:
	    * geneMap2.txt, http://www.omim.org/downloads
	    * mim2gene.txt, http://www.omim.org/downloads
	    * morbidmap, http://www.omim.org/downloads
	* Outfile(s): mimDisorderNodeOut.csv, mimDisorderRenOut.csv, mimEntrezRelnOut.csv, mimGeneNodeOut.csv, mimGeneRelnOut.csv
	* Imports: omimClasses.py module

## Various Ontologies

* ontologyParser.py
	* Parses files from multiple ontologies for neo4j graph database node and relationship creation.
	* Outfiles are .csv (pipe delimited) and generated with first line header of
    	node IDs, attributes, types and labels for neo4j-import tool
	* See howToRun() method for instructions using this script.
	* Infile(s) [ontology files in .obo format, 2015 versions used]:
	    * CHEBI Ontology, https://www.ebi.ac.uk/chebi/downloadsForward.do
	    * Disease Ontology, http://disease-ontologyorg/downloads/
	    * Gene Ontology, http://geneontologyorg/page/download-ontology
	    * Human Phenotype Ontology, http://human-phenotype-ontologygithub.io/downloads.html
	    * Mammalian Phenotype Ontology, http://obofoundry.org/ontology/mp.html
	    * Gene Ontology --> CHEBI Ontology, http://geneontologyorg/
	    * Plant Ontoogy, Plant Trait Ontology, http://www.plantontologyorg/download
	* Outfile(s): GOmfbp_to_ChEBI.csv, MPheno.ontology.csv, chebi_ontology.csv, disease_ontology.csv, gene_ontology.csv,
	    human_phenotype.csv, molecular_function_xp_chebi.csv, plant_trait_ontology.csv
	* Imports: ontologyClasses.py module