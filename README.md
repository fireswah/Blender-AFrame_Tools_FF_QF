# **Blender_FF_QF**
Blender tools for FastFuels and Quic-Fire

## **BlenderFastFuels**
This python script used in Blender creates quad or tri faced terrain and rewrites a treelist with elevation data at each tree location that can be used for data in other programs (like Unreal Engine in my workflow).
To run in full, it requires two outputs from FastFuels as data:
- FastFuels zarr array (contains the dem, elevations only)
- treelist.csv (unmodified with silvedits, contains the tree location and other data, but not elevation)

If you just want ground created from the zarr array, comment out the following lines at the end of the code:
```
#createTreePoints()
#createTrees( treesName )
#treesToTerrain( treesName, terrainName )
#writeNewTreeList()
```
### How To
+ Create a working folder
+ Create a Blender file and save/name it to folder
+ Copy outputs (treelist.csv and fuel-array.zip) to folder
+ Unzip fuel-array to same folder
+ Change to scripting view in Blender (top tab)
+ Click +New button to create a new script
+ Copy the BlenderFastFuels script in the code pane
+ Look at/edit the variables under SETUP OPTIONS
+ Press the Run Script button (looks like a play button at top)

