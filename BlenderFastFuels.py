"""
Author: Matt Gibson
    #This Blender 4, Python 3 script is used with output already created from FastFuels.
    #Python will need the zarr module installed (i.e.: pip -m install zarr).
        #If you have multiple versions of Python outside of Blender, renaming Blender's version
            #to a backup will default Blender to your main Python.  See:
            #https://blender.stackexchange.com/questions/5287/using-3rd-party-python-modules
    #Extract the fuel-array.zip in the same folder as your Blender file.
    #Put the treelist.csv into the same folder as well if doing trees.
    #+Y axis should be north (but needs further verifying).
"""

#IMPORT STATEMENTS
#You may need to install a couple more of these modules if you don't already have them.
import numpy as np
import bpy
import pathlib
import csv
import zarr
from math import pi

"""
SETUP OPTIONS
"""
#Clear current Collection in Blender
clearCollection = True
#Create the name of the file in quotes to name your output DEM csv.
outputDEM = 'elDdem.csv'
#DEM Resolution - Default from LANLGUI is 2M.  Don't change unless you changed in LANL.
demRes = 2
#'Quads' or 'Tris' for terrain generation
polyGen = 'Quads'
#Name of your original treelist.csv file
treefile = 'treelist_ElDTest.csv'
#Name of terrain object created in Collection
terrainName = 'el-dorado-ground'
#Name of tree object created in Collection
treesName = 'el-dorado-trees'
#Name of the new treelist.csv to write
newTreeFile = 'ElDoradoUnreal.csv'

"""
Variables, Blender Paths, References
"""
file_loc = pathlib.Path( __file__ ).parent.resolve() #this blender file
folder = pathlib.Path( file_loc ).parent.resolve() #folder file is in
data_coll = bpy.data.collections[ 'Collection' ] #name of collection in Blender Scene Collection (upper right)

csvdata = pathlib.Path( folder ).joinpath( outputDEM )
treedata = pathlib.Path( folder ).joinpath( treefile )
newtreedata = pathlib.Path( folder ).joinpath( newTreeFile )

vertices = []
edges = []
faces = []
treeverts = []
treeedges = []
treefaces = []
heightMax = 0
allTreeData = []
nx = 0 #This should match arraysize.txt output after running.  ElD = 437
ny = 0 #This should match arraysize.txt output after running.  ElD = 396

"""
Remap number range function
"""
def num_to_range( num, inMin, inMax, outMin, outMax ):
    return outMin + ( float( num - inMin ) / float(inMax - inMin ) * ( outMax - outMin ) )

"""
Creates .csv file of the elevation points from the zarr array.  Zarr only has elevation.
"""
def createElevCSV():
    fpath = pathlib.Path( folder ).joinpath( 'fuel-array/surface' )
    voxels = zarr.open( fpath )
    zarr_array_dem = voxels[ 'DEM' ]
    dem_data = np.array( zarr_array_dem )
    with open( csvdata, 'w' ) as f:
        np.savetxt( f, dem_data, fmt='%.4d', delimiter=",", newline='\n' )
    #print( zarr_array_dem.info )
    #print( str( "Array is " ) + str( len( dem_data ) ) + str( " items in length." ) )

"""
In Blender, this will clear the Collection of objects in the scene.
"""
def clearBlenderCollection():
    if clearCollection == True:
        for ob in data_coll.objects:
            bpy.data.objects.remove( ob )

"""
Terrain Polygon Generation
Remember that in the data it is Y, X!
"""
def generateDEMGrid(): 
    global heightMax
    global nx
    global ny
    with open( csvdata, 'r', newline='' ) as csvfile:
        datareader = csv.reader( csvfile )
        colRes = 0
        ny = 0
        for yValues in datareader:
            rowRes = 0
            nx = 0
            for index, elev in enumerate( yValues ):
                #get/set height for later use by trees.
                if int( elev ) > heightMax:
                   heightMax = int( elev )
                point = [ int( rowRes ), int( colRes ), int( elev ) ]
                vertices.append( point )
                rowRes += demRes
                nx += 1
            colRes += demRes
            ny += 1
        #print( ny ) #Use these to confirm against arraysize.txt output
        #print( nx )
    #Create faces as quadrangles or triangles    
    if polyGen == 'Quads':
        facerows = ny
        initialColumn = nx
        column = nx - 1
        rangeV = 0
        for frows in range( 0, facerows - 1 ):
            for v in range( rangeV, column ):
                poly = [ v, v + 1, v + initialColumn + 1, v + initialColumn ]
                faces.append( poly )
            rangeV = rangeV + initialColumn
            column = column + initialColumn
    elif polyGen == 'Tris':
        facerows = ny
        initialColumn = nx
        column = nx - 1
        rangeV = 0
        for frows in range( 0, facerows - 1 ):
            for v in range( rangeV, column ):
                tri1 = [ v, v + 1, v + initialColumn ]
                tri2 = [ v + 1, v + initialColumn + 1, v + initialColumn ]
                faces.append( tri1 )
                faces.append( tri2 )
            rangeV = rangeV + initialColumn
            column = column + initialColumn

"""
Blender terrain object creation
"""
def createGroundObject( name ):
    new_mesh = bpy.data.meshes.new( 'grounddata' )
    new_mesh.from_pydata( vertices, edges, faces )
    new_mesh.update()

    new_object = bpy.data.objects.new( name, new_mesh )
    data_coll.objects.link( new_object )

    bpy.data.objects[ name ].select_set( True )
    bpy.context.view_layer.objects.active = bpy.data.objects[ name ]
    bpy.ops.object.origin_set( type='GEOMETRY_ORIGIN', center='BOUNDS' )

"""
Create trees and place on terrain
"""    
def createTreePoints():
    with open( treedata, 'r', newline='' ) as csvfile:
        datareader = csv.reader( csvfile, delimiter=',' )
        next( csvfile )
        #Initialize max/min for x and y
        for init in datareader:
            maxX = float( init[ 7 ] )
            minX = float( init[ 7 ] )
            maxY = float( init[ 8 ] )
            minY = float( init[ 8 ] )
            #print(maxX, minX, maxY, minY)
            break
        
        #Reset reader and skip header row again
        csvfile.seek( 0 )
        next( csvfile )
        
        #Get max/min for x and y
        for row in datareader:
            if abs( float( row[ 7 ] ) ) > maxX:
                maxX = float( row[ 7 ] )
            if abs( float( row[ 7 ] ) ) < minX:
                minX = float( row[ 7 ] )       
            if abs( float( row[ 8 ] ) ) > maxY:
                maxY = float( row[ 8 ] )
            if abs( float( row[ 8 ] ) ) < minY:
                minY = float( row[ 8 ] )
            #print(maxX, minX, maxY, minY)

        #Set Ranges
        rangeX = float(maxX - minX)
        rangeY = float(maxY - minY)

        #Reset reader and skip header again
        csvfile.seek(0)
        next( csvfile )
        
        for tree in datareader:
            origX = float( tree [ 7 ] )
            origY = float( tree [ 8 ] )
            newX = num_to_range( origX, minX, maxX, 0, rangeX )
            newY = num_to_range( origY, minY, maxY, 0, rangeY )
            treepoint = [ newX, newY, heightMax ]
            treeverts.append( treepoint )
            allTreeData.append( [ tree[0], tree[1], tree[2], tree[3], tree[4], tree[5], tree[6], tree[7], tree[8], 0, tree[9] ] )
            #print(treeverts)

"""
Create Terrain and Trees in Blender viewport and shrinkwrap trees to terrain
"""
def createTrees( name ):
    new_mesh = bpy.data.meshes.new( 'treedata' )
    new_mesh.from_pydata( treeverts, treeedges, treefaces )
    new_mesh.update()

    new_object = bpy.data.objects.new( name, new_mesh )
    data_coll.objects.link( new_object )

    bpy.data.objects[ name ].select_set( True )
    bpy.context.view_layer.objects.active = bpy.data.objects[ name ]
    bpy.ops.object.origin_set( type='GEOMETRY_ORIGIN', center='BOUNDS' )
    bpy.ops.object.location = (0, 0, heightMax )

"""
treesToTerrain is Blender specific.  It adds a "shrinkwrap modifier" to the points on a negative Z axis
and moving them to where that intersects with the target (terrain).  Applying this modifier will automatically
change the vertex locations so we can get them back at elevation.
"""

def treesToTerrain( treeObject, target ):
    C = bpy.context
    obj = C.scene.objects[ treeObject ]
    bpy.context.view_layer.objects.active = bpy.data.objects[ treeObject ]
    shrink_mod = obj.modifiers.new( name='wrap', type='SHRINKWRAP')
    shrink_mod.wrap_method = 'PROJECT'
    shrink_mod.target = bpy.data.objects[ target ]
    shrink_mod.use_project_z = True
    shrink_mod.project_limit = 5000
    shrink_mod.use_negative_direction = True
    #Comment this last line if you need to adjust ground (but this should be fixed now).
    bpy.ops.object.modifier_apply( modifier = 'wrap' )

"""
Write new treelist with elevations included.
"""
def writeNewTreeList():
    newverts = []
    bpy.data.objects[ treesName ].select_set(True)
    obj = bpy.data.objects[ treesName ]
    for vert in obj.data.vertices:
        x, y, z = vert.co
        newverts.append( [x, y, z] )
    #print( len(vertZ) )
    with open( newtreedata, 'w', newline='' ) as newf:
        writer = csv.writer( newf )
        #Add header row to all tree data
        writer.writerow( [ 'ID','SPCD','DIA_cm','HT_m','STATUSCD','CBH_m','CROWN_RADIUS_m','X_m','Y_m','Z_m','basal_tree_ft^2' ] )
        #Write new csv using the new adjusted vert coordinates
        for atd, newv in zip( allTreeData, newverts):
            id = atd[0]
            spcd = atd[1]
            dia = atd[2]
            ht = atd[3]
            stat = atd[4]
            cbh = atd[5]
            crad = atd[6]
            #skip to 10.  7 and 8 were orig. x/y and 9 I added
            #in above as placeholder z in createTreePoints()
            bas = atd[10]
            newx = newv[0]
            newy = newv[1]
            newz = newv[2]
            writer.writerow( [ id, spcd, dia, ht, stat, cbh, crad, newx, newy, newz, bas ] )
    print( "Writing " + newTreeFile )

"""
Run it all in the order I built it.
"""
createElevCSV()
clearBlenderCollection()
generateDEMGrid()
createGroundObject( terrainName )
createTreePoints()
createTrees( treesName )
treesToTerrain( treesName, terrainName )
writeNewTreeList()