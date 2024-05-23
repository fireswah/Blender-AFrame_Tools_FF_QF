import bpy
import pathlib
import csv

"""
SETUP OPTIONS
"""
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
newtreedata = pathlib.Path( folder ).joinpath( newTreeFile )

def writeNewTreeList():
    newverts = []
    obj = bpy.data.objects[ treesName ]
    mesh = obj.data

    with open( newtreedata, 'w', newline='' ) as newf:
        writer = csv.writer( newf )
        #Add header row to all tree data
        writer.writerow( [ '','SPCD','DIA_cm','HT_m','STATUSCD','CBH_m','CROWN_RADIUS_m','X_m','Y_m','Z_m','basal_tree_ft^2' ] )
        #Write new csv using the new adjusted vert coordinates
        for idx, vert in enumerate( mesh.vertices ):
            x,y, z = vert.co
            id = mesh.attributes[ 'ID' ].data[ idx ].value
            spcd = mesh.attributes[ 'SPCD' ].data[ idx ].value
            dia = mesh.attributes[ 'DIA_cm' ].data[ idx ].value
            ht = mesh.attributes[ 'HT_m' ].data[ idx ].value
            stat = mesh.attributes[ 'STATUSCD' ].data[ idx ].value
            cbh = mesh.attributes[ 'CBH_m' ].data[ idx ].value
            crad = mesh.attributes[ 'CROWN_RADIUS_m' ].data[ idx ].value
            newx = x
            newy = y
            newz = z
            bas = mesh.attributes[ 'basal_tree_ft^2' ].data[ idx ].value
            writer.writerow( [ id, spcd, dia, ht, stat, cbh, crad, newx, newy, newz, bas ] )
    print( "Writing " + newTreeFile )

writeNewTreeList()