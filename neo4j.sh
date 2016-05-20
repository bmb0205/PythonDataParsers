#!/bin/bash

# Remove any previous database version to prepare for import into Neo4j
rm -r /home/bmb0205/NEO4J/neo4j-community-2.3.2/data/graph.db/* \

# neo4j-import to load delimited parsed data into Neo4j graph database
/home/bmb0205/NEO4J/neo4j-community-2.3.2/bin/./neo4j-import \
--into /home/bmb0205/NEO4J/neo4j-community-2.3.2/data/graph.db/ \
--delimiter '|' \
--stacktrace 'true' \
--nodes '/home/bmb0205/BiSD/KnowledgeBase/notouch/outfiles/Mammalian_Phenotype_Ontology.csv' \
--nodes '/home/bmb0205/BiSD/KnowledgeBase/notouch/outfiles/Plant_Ontology.csv' \
--nodes '/home/bmb0205/BiSD/KnowledgeBase/notouch/outfiles/chebi_ontology.csv' \
--nodes '/home/bmb0205/BiSD/KnowledgeBase/notouch/outfiles/disease_ontology.csv' \
--nodes '/home/bmb0205/BiSD/KnowledgeBase/notouch/outfiles/gene_ontology.csv' \
--nodes '/home/bmb0205/BiSD/KnowledgeBase/notouch/outfiles/human_phenotype.csv' \
--nodes '/home/bmb0205/BiSD/KnowledgeBase/notouch/outfiles/plant_trait_ontology.csv' \
--relationships '/home/bmb0205/BiSD/KnowledgeBase/notouch/outfiles/oboRelnOut.csv' \
--nodes '/home/bmb0205/BiSD/KnowledgeBase/notouch/outfiles/meshNodeOut.csv' \
--relationships '/home/bmb0205/BiSD/KnowledgeBase/notouch/outfiles/meshRelnOut.csv' \
--nodes '/home/bmb0205/BiSD/KnowledgeBase/notouch/outfiles/nalNodeOut.csv' \
--relationships '/home/bmb0205/BiSD/KnowledgeBase/notouch/outfiles/nalRelnOut.csv' \
--nodes '/home/bmb0205/BiSD/KnowledgeBase/notouch/outfiles/taxNodeOut.csv' \
--relationships '/home/bmb0205/BiSD/KnowledgeBase/notouch/outfiles/taxRelnOut.csv' \
--nodes '/home/bmb0205/BiSD/KnowledgeBase/notouch/outfiles/ttdNodeOut.csv' \
--relationships '/home/bmb0205/BiSD/KnowledgeBase/notouch/outfiles/targetKEGGRelnOut.csv' \
--relationships '/home/bmb0205/BiSD/KnowledgeBase/notouch/outfiles/targetWikiRelnOut.csv' \
--nodes '/home/bmb0205/BiSD/KnowledgeBase/notouch/outfiles/ttdNodeOut2.csv' \
--nodes '/home/bmb0205/BiSD/KnowledgeBase/notouch/outfiles/wikiNodeOut.csv' \
--nodes '/home/bmb0205/BiSD/KnowledgeBase/notouch/outfiles/KEGGNodeOut.csv' \
--nodes '/home/bmb0205/BiSD/KnowledgeBase/Sources/csv_out/All_Mammalia.gene_info.out' \
--nodes '/home/bmb0205/BiSD/KnowledgeBase/Sources/csv_out/All_Plants.gene_info.out' \
--relationships '/home/bmb0205/BiSD/KnowledgeBase/Sources/csv_out/gene2go.out' \
--relationships '/home/bmb0205/BiSD/KnowledgeBase/Sources/csv_out/gene_group.out'