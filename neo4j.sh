#!/bin/bash

outfileDir='/home/bmb0205/BiSD/KnowledgeBase/notouch/outfiles/'
outfileDir2='/home/bmb0205/BiSD/KnowledgeBase/Sources/csv_out/'

# Remove any previous database version to prepare for import into Neo4j
rm -r '/home/bmb0205/apps/NEO4J/neo4j-community-2.3.2/data/graph.db/' \

# neo4j-import to load delimited parsed data into Neo4j graph database
/home/bmb0205/apps/NEO4J/neo4j-community-2.3.2/bin/./neo4j-import \
--into /home/bmb0205/apps/NEO4J/neo4j-community-2.3.2/data/graph.db/ \
--delimiter '|' \
--stacktrace 'true' \
--nodes $outfileDir'Mammalian_Phenotype_Ontology.csv' \
--nodes $outfileDir'Plant_Ontology.csv' \
--nodes $outfileDir'chebi_ontology.csv' \
--nodes $outfileDir'disease_ontology.csv' \
--nodes $outfileDir'gene_ontology.csv' \
--nodes $outfileDir'human_phenotype.csv' \
--nodes $outfileDir'plant_trait_ontology.csv' \
--relationships $outfileDir'oboRelnOut.csv' \
--nodes $outfileDir'meshNodeOut.csv' \
--relationships $outfileDir'meshRelnOut.csv' \
--nodes $outfileDir'nalNodeOut.csv' \
--relationships $outfileDir'nalRelnOut.csv' \
--nodes $outfileDir'taxNodeOut.csv' \
--relationships $outfileDir'taxRelnOut.csv' \
--nodes $outfileDir'ttdNodeOut.csv' \
--relationships $outfileDir'targetKEGGRelnOut.csv' \
--relationships $outfileDir'targetWikiRelnOut.csv' \
--nodes $outfileDir'ttdNodeOut2.csv' \
--nodes $outfileDir'wikiNodeOut.csv' \
--nodes $outfileDir'KEGGNodeOut.csv' \
--nodes $outfileDir2'All_Mammalia.gene_info.out' \
--nodes $outfileDir2'All_Plants.gene_info.out' \
--relationships $outfileDir'gene2go.out' \
--relationships $outfileDir'/gene_group.out'