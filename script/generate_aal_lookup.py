# script to generate coordinate lookup

import pandas
import nibabel
import requests
import xmltodict
from nilearn.image import resample_img
from nilearn.plotting import find_xyz_cut_coords

# OBTAIN AAL2 ATLAS FROM NEUROVAULT

data = nibabel.load("AAL2_2.nii.gz")
img4mm = nibabel.load("MNI152_T1_4mm_brain_mask.nii.gz")

# Use nilearn to resample - nearest neighbor interpolation to maintain atlas
aal4mm = resample_img(data,interpolation="nearest",target_affine=img4mm.get_affine())

# Get labels
labels = numpy.unique(aal4mm.get_data()).tolist()

# We don't want to keep 0 as a label
labels.sort()
labels.pop(0)

# OBTAIN LABEL DESCRIPTIONS WITH NEUROVAULT API
url = "http://neurovault.org/api/atlases/14255/?format=json"
response = requests.get(url).json()

# This is an xml file with label descriptions
xml = requests.get(response["label_description_file"])
doc = xmltodict.parse(xml.text)["atlas"]["data"]["label"]  # convert to a superior data structure :)

# We will store region voxel value, name, and a center coordinate
regions = pandas.DataFrame(columns=["value","name","x","y","z"])

count = 0
for region in doc:
    regions.loc[count,"value"] = int(region["index"]) 
    regions.loc[count,"name"] = region["name"] 
    count+=1

# USE NILEARN TO FIND REGION COORDINATES (the center of the largest activation connected component)
for region in regions.iterrows():
    label = region[1]["value"]
    roi = numpy.zeros(aal4mm.shape)
    roi[aal4mm.get_data()==label] = 1
    nii = nibabel.Nifti1Image(roi,affine=aal4mm.get_affine())
    x,y,z = [int(x) for x in find_xyz_cut_coords(nii)]
    regions.loc[region[0],["x","y","z"]] = [x,y,z]

# Save data to file for application
regions.to_csv("../data/aal_4mm_region_coords.tsv",sep="\t")

# We will also flatten the brain-masked imaging data into a vector,
# so we can select a region x,y,z based on the name
region_lookup = pandas.DataFrame(columns=["aal"])
region_lookup["aal"] = aal4mm.get_data()[img4mm.get_data()!=0]

region_lookup.to_pickle("../data/aal_4mm_region_lookup.pkl")
