from flask import Flask, render_template
import random
import numpy
import pandas
import pickle
import json

# SERVER CONFIGURATION ##############################################
class CogatServer(Flask):

    def __init__(self, *args, **kwargs):
            super(CogatServer, self).__init__(*args, **kwargs)

            # load data on start of application
            self.df = pandas.read_pickle("data/regression_params.pkl")
            self.images = pandas.read_csv("data/contrast_defined_images_filtered.tsv",sep="\t",index_col="image_id")
            self.Y = pandas.read_csv("data/images_contrasts_df.tsv",sep="\t",index_col=0)
            self.lookup = pandas.read_csv("data/cogatlas_concepts.tsv",sep="\t",index_col=0)
            self.regions = pandas.read_csv("data/aal_4mm_region_coords.tsv",sep="\t",index_col=0)
            self.region_lookup = pandas.read_pickle("data/aal_4mm_region_lookup.pkl")
            self.tree = pickle.load(open("data/concepts.pkl","r"))

            # D3 specific variables
            self.width = 1500
            self.height = 600
            self.padding = 12
            self.maxRadius = 30
          
            # Image data
            self.X = pickle.load(open("data/images_df.pkl","rb"))
            # value will be radius, we don't want negative values
            self.radius = self.X + self.X.min().abs()

            # Pairwise spatial similarity
            self.spatial = pandas.read_csv("data/contrast_defined_images_pearsonpd_similarity.tsv",sep="\t",index_col=0)

app = CogatServer(__name__)

# Global variables for app

### Helper Functions
def make_node(concept,tagged_image,v):
  image = app.images.loc[tagged_image]
  classes = " ".join(app.Y.loc[tagged_image][app.Y.loc[tagged_image]==1].index.tolist())
  return {
    "radius": app.radius.loc[tagged_image,v],
    "concept": concept,
    "concept_name":app.lookup.name[app.lookup.id==concept].tolist()[0],
    "classes":classes,
    "contrast": image.cognitive_contrast_cogatlas,
    "task": image.cognitive_paradigm_cogatlas,
    "collection": image.collection_id,
    "thumbnail": image.thumbnail,
    "value": app.X.loc[tagged_image,v],
    "uid":tagged_image
   }

def get_lookup():
    lookup = dict()
    for row in app.lookup.iterrows():
        lookup[row[1].id] = row[1]["name"] #cannot be .name
    return lookup

def get_counts():
    counts = dict()
    for concept in app.Y.columns:
        counts[concept] = app.Y[concept].sum()
    min_count = numpy.min(counts.values())
    max_count = numpy.max(counts.values())
    return counts,min_count,max_count

def random_colors(concepts):
    '''Generate N random colors'''
    colors = {}
    for x in range(len(concepts)):
        concept = concepts[x]
        r = lambda: random.randint(0,255)
        colors[concept] = '#%02X%02X%02X' % (r(),r(),r())
    return colors


@app.route("/<v>")
def voxel(v,name):

    v = int(v)

    # Prepare variables
    regparams = app.df.loc[v]

    # We are only interested in nonzero concepts
    concepts = regparams.index.tolist()
    colors = random_colors(concepts)
    regparams = regparams.to_json()

    nodes = []
    unique_images = []  
    # prepare list of images for each concept
    for concept in concepts:
        tagged_images = app.Y.index[app.Y[concept]==1].tolist() 
        for tagged_image in tagged_images:
            nodes.append(make_node(concept,tagged_image,v))
            if tagged_image not in unique_images:
                unique_images.append(tagged_image)

    # Generate a lookup for concept names and counts
    lookup = get_lookup()
    counts,min_count,max_count = get_counts()

    # Min and max values for the color scale
    min_voxel = app.X.loc[:,v].min()
    max_voxel = app.X.loc[:,v].max()

    # We only need spatial similarity for images relevant to concept
    spatial = app.spatial.loc[unique_images,[str(x) for x in unique_images]]
    spatial = (spatial-1).abs().to_json() # needs to be a positive distance between 0 and 1

    # We will let the user select a voxel location based on region
    regions = app.regions.to_dict(orient="records")

    return render_template("index.html",regparams=regparams,
                                        M=len(concepts),
                                        N=len(nodes),
                                        min=app.df.loc[v].min(),
                                        max=app.df.loc[v].max(),
                                        width=app.width,
                                        min_voxel=min_voxel,
                                        max_voxel=max_voxel,
                                        height=app.height,
                                        padding=app.padding,
                                        counts=counts,
                                        max_count=max_count,
                                        min_count=min_count,
                                        radius=app.radius,
                                        maxRadius=app.maxRadius,
                                        nodes=nodes,
                                        spatial=spatial,
                                        lookup=lookup,
                                        colors=colors,
                                        voxel=v,
                                        regions=regions,
                                        region_name=name,
                                        tree=app.tree)


@app.route("/")
def index():
    # Select a random region
    name = numpy.random.choice(app.regions.name.tolist(),1)[0]
    return region(name)


@app.route("/region/<name>")
def region(name):

    # Look up the value of the region
    value = app.regions.value[app.regions.name==name].tolist()[0]
    
    # Select a voxel coordinate at random
    voxel_idx = numpy.random.choice(app.region_lookup.index[app.region_lookup.aal == value],1)[0]

    return voxel(voxel_idx,name=name)

if __name__ == "__main__":
    app.debug = True
    app.run()

