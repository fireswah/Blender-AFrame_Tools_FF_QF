# **Blender-AFrame_Tools_FF_QF**
Blender and AFrame tools for FastFuels and Quic-Fire

## **BlenderFastFuels**
This Python3 script used in Blender4+ :
- Reads a fuel-array.zip zarr file from FastFuels to create a quad or tri faced mesh of the terrain
- Reads a treelist.csv from FastFuels and creates a points object of the trees containing all the data in the .csv on a per vertex basis
- Once it's run in Blender, you can then delete "trees" by selecting and deleting the points.
- Sets both terrain and fuels objects to the same extent, centers them at center of Blender scene, uses a Shrinkwrap modifier to set the trees on the terrain at the correct elevation.
 
To run in full, it requires two outputs from FastFuels as data:
- FastFuels zarr array (contains the dem elevations and grid size/spacing (no need to unzip).
- treelist.csv (contains the tree location and other data, but not elevation)
- NOTE: This script will not yet work on a treelist with "silvedits" already made in the LANL tool.  There is a slight data difference between the two .csv's, so use the main treelist.

If you just want ground created from the zarr array, comment out the following lines at the end of the code:
```
#createTreePoints()
#createTrees( treesName )
#treesToTerrain( treesName, terrainName )
```
### How To
+ Create a working folder
+ Create a Blender file and save/name it to folder
+ Copy outputs (treelist.csv and fuel-array.zip) to folder
+ Change to scripting view in Blender (top tab)
+ Click +New button to create a new script
+ Copy the BlenderFastFuels script in the code pane
+ Look at/edit the variables under SETUP OPTIONS
+ Press the Run Script button (looks like a play button at top)

### Writing A New Modified Treelist.csv After Editing
After making edits to your fuels in Blender, you can run the WriteNewTreeList.py script in the same Blender file.
+ Go back into scripting mode in your Blender file
+ Click on the New Text button (looks like a pages icon)
+ Paste the other script into the code window
+ Make sure you edit/update the two SETUP OPTIONS to match your data.
+ Run it

This will produce a new .csv containing your modified treelist data.
Headers for this .csv are different because it will add the height for each tree on the list.  Format is:
```
'',SPCD,DIA_cm,HT_m,STATUSCD,CBH_m,CROWN_RADIUS_m,X_m,Y_m,Z_m,basal_tree_ft^2
```
IMPORTANT:
x, y, and z values on your exported .csv will be 3D space modified instead of lat/lon/elevation.  The intent of this script isn't to retain the original data, but rather for use in 3D visualization tools like AFrame, Unreal Engine, Unity, etc.  I may add an option later to retain the original lat/lon as well. 

##tree-builder-points.js
This is an AFrame DEMO component that
+ Reads a Blender modified (z enabled) treelist.csv.
+ Groups species of trees into a Three.js bufferattribute
+ Displays trees as a point.  The image is of a whole tree and is scaled according to the treelist data.  The tree images used are in the treeTextureAtlas.png file and the custom glsl shader changes the uv values to utilize the atlas.
IMPORTANT:
This is a demo and only accounts for a few species at this point.

Include AFrame and the tree builder script in html:
```
<script src="https://aframe.io/releases/1.5.0/aframe.min.js"></script>
<script src="./scripts/tree-builder-points.js"></script>
```
Load your treelist.csv as an AFrame asset in html:
```
<a-asset-item id="treesheet" src="./data/ElDoradoUnreal.csv"></a-asset-item>  <!-- For now, don't change the treesheet id name -->
```
Create an entity with the component added in html:
```
<a-entity id="trees" position="0 0 0" tree-builder></a-entity>
```

