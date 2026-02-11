# **Blender-AFrame_Tools_FF_QF**
Blender and AFrame tools for FastFuels

## **FastFuels To Blender**
**The FastFuels To Blender workflow represents an interim step in visualizing landscape and vegation domains, while the FastFuels system continues to work towards making the data available for all.  Eventually the data the script retrieves will be available as an export from the FastFuels user interface.**

**NOTES:**
- This script will not work with a fuelarray.zip from the QuicFire output files.  It is designed to work directly with the FastFuels API (https://api.fastfuels.silvxlabs.com/redoc)
- You will need a FastFuels account: https://fastfuels.silvxlabs.com/
- You will need a FastFuels personal API key with write access: https://docs.fastfuels.silvxlabs.com/home/
- You will need the two files in the FastFuels To Blender folder, where you will find a python script (.py) and Blender File (.blend)
- The FastFuels system can do very large domains, however, the script is designed for "non-chunked" domains, and I recommend while using this workflow keeping domain size around the ~500 acre size.  Your mileage will vary with your computer's CPU and GPU capability.

#### The Pyhton script:
- Gets topography for your domain in geotiff format
- Provides the NX, NY (horizontal) and elevation range (vertical) information for your topography
- Creates road and water features for your domain (this helps improve the final tree inventory data)
- Creates a tree inventory and download as a .csv file
- Creates an adjusted treelist based on the original, converting lat/long info to 3D space and replacing "null" values with 0 for import into other systems
- Uses the domain information and retrieves a custom NAIP image from The National Map image servers for texturing the terrain with in the same CRS of the domain.

#### The Blender file:
- Uses Geometry Nodes (visual scripting) to import terrain and fuels, setup with simple inputs from the data retrieved with the FastFuels script
- The Grid Nodes use NX, NY and Elevation Range with a converted geotiff (see how to) to make a terrain mesh
- The Trees Nodes import the adjusted treelist.csv, raycasts them against the terrain mesh, and places a 3D object at each tree based on the data.  "Live" trees will be displayed as green, and "dead" trees will be displayed in gray. 

### How To
+ Visit YouTube here for the workflow video: https://www.youtube.com/watch?v=6BFdTKDuPvA

## **/AFrame Components/tree-builder-points-component.js**
This is an AFrame DEMO component that
+ Reads a Blender modified (z enabled) treelist.csv.
+ Groups species of trees into separate Three.js points geometries.
+ If no species image path match exists, creates a random color points geometry for that species. (i.e. all Douglas Fir would be blue, etc.)  This will be random each time the scene is run right now.
+ Displays trees as a point.  The image is of a whole tree and is scaled according treelist data (Ht_m).  The tree images used are in the images folder.
+ Each species points has it's own glsl shader rather than using a texture atlas.

Include AFrame and the tree builder script in html:
```
<script src="https://aframe.io/releases/1.5.0/aframe.min.js"></script>
<script src="./scripts/tree-builder-points-component.js"></script>
```
Load your treelist.csv as an AFrame asset in html:
```
<a-asset-item id="treesheet" src="./data/ElDoradoUnreal.csv"></a-asset-item>  <!-- For now, don't change the treesheet id name -->
```
Create an entity with the component added in html:
```
<a-entity id="trees" position="0 0 0" tree-builder></a-entity>
```
Download (see /images below) or create a subfolder called images and place your own tree images in it.

### Notes
The treelist must be "z-enabled".  See the Blender tools section if you need to create one.
This is a demo and only accounts for a few species at this point.
Images were rendered from Blender sapling high poly trees, eyeballed from photos on the web.

## **/images**
This folder contains whole tree images for use with the AFrame tree-builder-points-component.js.  It is also intended to be a working test of filenames for tree species.

### How To Use
Download the folder and place within your AFrame folder structure for a given scene.

### Notes
The ./image file path hard coded in the tree component.  If you change the name of the folder, you'll have to update the file paths for trees in the component as well.

