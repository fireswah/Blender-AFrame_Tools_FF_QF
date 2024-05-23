"""
Author: Matt Gibson
    #This Blender 4 Python 3 script is for use with a FastFuels zarr array
    #Python will need the zarr module installed (i.e.: pip -m install zarr).
        #If you have multiple versions of Python outside of Blender, renaming Blender's version
            #to a backup will default Blender to your main Python.  See:
            #https://blender.stackexchange.com/questions/5287/using-3rd-party-python-modules
    #Put the fuel-array.zip into the same folder as your Blender file.
    #Put the treelist.csv into the same folder as well if doing trees.
    #Blender +Y axis should be north (but needs further verifying).
"""

#IMPORT STATEMENTS
#You may need to install a couple more of these modules if you don't already have them.
import numpy as np
import bpy
import pathlib
import csv
import zarr

"""
SETUP OPTIONS
"""
#Clear current Collection in Blender
clearCollection = True
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
newTreeFile = 'ElDoradoExport.csv'

"""
Variables, Blender Paths, References
"""
file_loc = pathlib.Path( __file__ ).parent.resolve() #this blender file
folder = pathlib.Path( file_loc ).parent.resolve() #folder file is in
data_coll = bpy.data.collections[ 'Collection' ] #name of collection in Blender Scene Collection (upper right)
treedata = pathlib.Path( folder ).joinpath( treefile )
newtreedata = pathlib.Path( folder ).joinpath( newTreeFile )

ny = 0
nx = 0
xmax = 0
xmin = 0
ymax = 0
ymin = 0
zmax = 0
zmin = 0
xRange = 0
yRange = 0
zRange = 0

demVerts = []
demFaces = []
treeVerts = []
treeEdges = []
treeFaces = []
allTreeData = []

"""
In Blender, this will clear the Collection of objects in the scene.
"""
def clearBlenderCollection():
    if clearCollection == True:
        for ob in data_coll.objects:
            bpy.data.objects.remove( ob )

"""
Remap number range function
"""
def num_to_range( num, inMin, inMax, outMin, outMax ):
    return outMin + ( float( num - inMin ) / float(inMax - inMin ) * ( outMax - outMin ) )

"""
Creates a Quad or Tri faced terrain object utilizing the zarr array only
*Still need to address "bounds" from FF and test?
"""
def generateDEMGrid( ny, nx, xmin, ymin, heightarray ): 
    y = ymin
    print(ny, nx)
    for a in range(ny):
        x = xmin
        for b in range(nx):
            #Blender posX - left, poxY - towards viewer, posz - up
            point = [ x, y, heightarray[ a ][ b ] ]
            demVerts.append( point )
            x = x + demRes
        y = y + demRes
    #Quads and Tris working, but I still need to clean them up better so they are less confusing!
    if polyGen == 'Quads':
        facerows = ny
        initialColumn = nx
        column = nx - 1
        rangeV = 0
        for frows in range( 0, facerows - 1 ):
            for v in range( rangeV, column ):
                poly = [ v, v + 1, v + initialColumn + 1, v + initialColumn ]
                demFaces.append( poly )
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
                demFaces.append( tri1 )
                demFaces.append( tri2 )
            rangeV = rangeV + initialColumn
            column = column + initialColumn

"""
Blender create ground in collection, set origin
"""
def createGroundObject( name ):
    new_mesh = bpy.data.meshes.new( 'grounddata' )
    new_mesh.from_pydata( demVerts, [], demFaces )
    new_mesh.update()

    new_object = bpy.data.objects.new( name, new_mesh )
    data_coll.objects.link( new_object )

    bpy.data.objects[ name ].select_set( True )
    bpy.context.view_layer.objects.active = bpy.data.objects[ name ]
    bpy.ops.object.origin_set( type='GEOMETRY_ORIGIN', center='BOUNDS' )

"""
Create Tree Points from original .csv lat/lons.
*The terrain matches the bounding box of trees already now.
"""
def createTreePoints():
    with open( treedata, 'r', newline='' ) as csvfile:
        datareader = csv.reader( csvfile, delimiter=',' )
        next( csvfile )#skip header row
        for tree in datareader:
            origX = float( tree [ 7 ] )
            origY = float( tree [ 8 ] )
            treepoint = [ origX, origY, 0 ]
            treeVerts.append( treepoint )
            allTreeData.append( [ tree[0], tree[1], tree[2], tree[3], tree[4], tree[5], tree[6], tree[7], tree[8], 0, tree[9] ] )

"""
Blender create trees in collection, add per vertex attribtue data set origin
"""
def createTrees( name ):
    #Create the trees as a mesh of points and add to scene
    new_mesh = bpy.data.meshes.new( 'treedata' )
    new_mesh.from_pydata( treeVerts, treeEdges, treeFaces )
    new_mesh.update()
    new_object = bpy.data.objects.new( name, new_mesh )
    data_coll.objects.link( new_object )

    #set original tree data as attributes on each vertex(data will be in model now, instead of just memory/csv)
    ids = []
    spcd = []
    dia = []
    ht = []
    status = []
    cbh = []
    crownrad = []
    xM = []
    yM = []
    bas = []

    obj = bpy.context.scene.objects[ name ]
    attrID = obj.data.attributes.new( name="ID", type="INT", domain="POINT" )
    attrSPCD = obj.data.attributes.new( name="SPCD", type="INT", domain="POINT" )
    attrDIA = obj.data.attributes.new( name="DIA_cm", type="FLOAT", domain="POINT" )
    attrHT = obj.data.attributes.new( name="HT_m", type="FLOAT", domain="POINT" )
    attrSTATUS = obj.data.attributes.new( name="STATUSCD", type="INT", domain="POINT" )
    attrCBH = obj.data.attributes.new( name="CBH_m", type="FLOAT", domain="POINT" )
    attrCROWNR = obj.data.attributes.new( name="CROWN_RADIUS_m", type="FLOAT", domain="POINT" )
    attrX = obj.data.attributes.new( name="X_m", type="FLOAT", domain="POINT" )
    attrY = obj.data.attributes.new( name="Y_m", type="FLOAT", domain="POINT" )
    attrBAS = obj.data.attributes.new( name="basal_tree_ft^2", type="FLOAT", domain="POINT" )
    for i in range( len( obj.data.vertices ) ):
        ids.append( int( allTreeData[ i ][ 0 ] ) )
        spcd.append( int( allTreeData[ i ][ 1 ] ) )
        if allTreeData[ i ][ 2 ] == '':
            dia.append( float( 0 ) )
        else:
            dia.append( float( allTreeData[ i ][ 2 ] ) )
        if allTreeData[ i ][ 3 ] == '':
            ht.append( float( 0 ) )
        else:
            ht.append( float( allTreeData[ i ][ 3 ] ) )
        if allTreeData[ i ][ 4 ] == '':
            status.append( int( 0 ) )
        else:
            status.append( int( allTreeData[ i ][ 4 ] ) )
        if allTreeData[ i ][ 5 ] == '':
            cbh.append( float( 0 ) )
        else:
            cbh.append( float( allTreeData[ i ][ 5 ] ) )
        if allTreeData[ i ][ 6 ] == '':
            crownrad.append( float( 0 ) )
        else:
            crownrad.append( float( allTreeData[ i ][ 6 ] ) )
        xM.append( float( allTreeData[ i ][ 7 ] ) )
        yM.append( float( allTreeData[ i ][ 8 ] ) )
        if allTreeData[ i ][ 9 ] == '':
            bas.append( float( 0 ) )
        else:
            bas.append( float( allTreeData[ i ][ 9 ] ) )
    obj.data.attributes[ 'ID' ].data.foreach_set( "value", ids )
    obj.data.attributes[ 'SPCD' ].data.foreach_set( "value", spcd )
    obj.data.attributes[ 'DIA_cm' ].data.foreach_set( "value", dia )
    obj.data.attributes[ 'HT_m' ].data.foreach_set( "value", ht )
    obj.data.attributes[ 'STATUSCD' ].data.foreach_set( "value", status )
    obj.data.attributes[ 'CBH_m' ].data.foreach_set( "value", cbh )
    obj.data.attributes[ 'CROWN_RADIUS_m' ].data.foreach_set( "value", crownrad )
    obj.data.attributes[ 'X_m' ].data.foreach_set( "value", xM )
    obj.data.attributes[ 'Y_m' ].data.foreach_set( "value", yM )
    obj.data.attributes[ 'basal_tree_ft^2' ].data.foreach_set( "value", bas )

    #Move tree points to origin from original lat/lon and set above terrain for next step.
    bpy.data.objects[ name ].select_set( True )
    bpy.context.view_layer.objects.active = bpy.data.objects[ name ]
    bpy.ops.object.origin_set( type='GEOMETRY_ORIGIN', center='BOUNDS' )
    bpy.ops.object.location = (0, 0, 2000 )#set high so it's above highest terrain point

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
Zarr info and data set variables
"""
fpath = pathlib.Path( folder ).joinpath( 'fuel-array.zip' )
zarr_root = zarr.open( fpath )
attrs = zarr_root.attrs
ny = attrs[ 'ny' ]
nx = attrs[ 'nx' ]
xmax = attrs[ 'xmax' ]
xmin = attrs[ 'xmin' ]
ymax = attrs[ 'ymax' ]
ymin = attrs[ 'ymin' ]
xRange = xmax - xmin
yRange = ymax - ymin
surface = zarr_root.surface
dem = surface[ 'DEM' ]
npheightarray = dem[...]
zmax = np.max( npheightarray )
zmin = np.min( npheightarray )
zRange = zmax - zmin

"""
Run it all in the order I built it.
"""
clearBlenderCollection()
generateDEMGrid( int(ny), int(nx), int(xmin), int(ymin), npheightarray )
createGroundObject( terrainName )
createTreePoints()
createTrees( treesName )
treesToTerrain( treesName, terrainName )
