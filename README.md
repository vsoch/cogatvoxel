# Cognitive Atlas Voxel Visualization

### Running

Without Docker

      cd cogat_voxel
      python index.py


With Docker

      git clone http://www.github.com/vsoch/cogat_voxel
      cd cogat_voxel
      docker-compose up -d


Then go to http://127.0.0.1:5000/ in your browser.


### About the Visualization
The visualization allows you to see the cognitive concepts that are associated with each voxel (a spatial location indicated by an x,y,z coordinate) in the brain. Each node (circle) that you see in the m

### Early Notes

I thought about this last night, and I think I know what I'm going to try. I think that the best strategy, akin to the figure 2, is to make the visualization on the level of the voxel. Eg: imagine an interactive interface where you can click around the brain, and produce a different visualization depending on where you click. The visualization will be very simple - because there are two things we want to show. 1) is relationships between concepts, specifically for that voxel. 2) is the relationship between different contrasts, and then how those contrasts are represented by the concepts. The first data that we have that is meaningful for the viewer are the tagged contrasts. For each contrast, we have two things: an actual voxel value from the map, and a similarity metric to all other contrasts (spatial and/or semantic). A simple visualization would produce some clustering to show to the viewer how the concepts are similar / different based on distance. The next data that we have "within" a voxel is information about concepts at that voxel (and this is where the model is integrated). Specifically - a vector of regression parameters for that single voxel. These regression parameter values are produced via the actual voxel values at the map (so we probably would not use both). What I think we want to do is have two clusterings - first cluster the concepts, and then within each concept bubble, show a smaller clustering of the images, clustered via similarity, and colored based on the actual value in the image (probably some shade of red or blue).
