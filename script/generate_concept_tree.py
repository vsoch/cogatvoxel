from pybraincompare.ontology.tree import named_ontology_tree_from_tsv
from cognitiveatlas.datastructure import concept_node_triples
import pickle
import pandas
import re

# Read in images metadata
images = pandas.read_csv("../data/contrast_defined_images_filtered.tsv",sep="\t",index_col="image_id")

## STEP 1: GENERATE TRIPLES DATA STRUCTURE

'''
  id    parent  name
  1 none BASE                   # there is always a base node
  2 1   MEMORY                  # high level concept groups
  3 1   PERCEPTION              
  4 2   WORKING MEMORY          # concepts
  5 2   LONG TERM MEMORY
  6 4   image1.nii.gz           # associated images (discovered by way of contrasts)
  7 4   image2.nii.gz
'''

# We need a dictionary to look up image lists by contrast ids
unique_contrasts = images.cognitive_contrast_cogatlas_id.unique().tolist()

# Images that do not match the correct identifier will not be used (eg, "Other")
expression = re.compile("cnt_*")
unique_contrasts = [u for u in unique_contrasts if expression.match(u)]

image_lookup = dict()
for u in unique_contrasts:
   image_lookup[u] = images.index[images.cognitive_contrast_cogatlas_id==u].tolist()

output_triples_file = "../data/concepts.tsv"

# Create a data structure of tasks and contrasts for our analysis
relationship_table = concept_node_triples(image_dict=image_lookup,output_file=output_triples_file)

# We don't want to keep the images on the tree
keep_nodes = [x for x in relationship_table.id.tolist() if not re.search("node_",x)]
relationship_table = relationship_table[relationship_table.id.isin(keep_nodes)]

tree = named_ontology_tree_from_tsv(relationship_table,output_json=None)
pickle.dump(tree,open("../data/concepts.pkl","w"))
json.dump(tree,open("../static/concepts.json",'w'))
