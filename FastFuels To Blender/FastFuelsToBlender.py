"""
This script utilizes the FastFuels API in combination with the Fastfuels webmap 
and the NAIP imageserver as part of a rapid (~10 minute workflow) to produce 3D
landscapes with tree vegetation.  Visualization occurs in Blender in the other half
of the workflow and can be exported for use in other systems.
"""
import requests
import time
import json
import csv

#####
#Set these variables:
ffprojectname = "" #needs to match your ff domain name in the web browser
ffapikey = ""
#####

#Don't change the following, they'll be updated when you run the script.
uniqueID = ''
headers = {
        "accept": "application/json",
        "api-key": ffapikey,
        "Content-Type": "application/json",
    }
nX = 0
nY = 0
scriptStart = time.time()

def getProjectID():
    """
    This api call gets the unique ID of the domain you created in the web app by name
    """
    global uniqueID
    
    url = "https://api.fastfuels.silvxlabs.com/v1/domains"

    params = {
        "page": 0,
        "size": 100,
        "sortBy": "name",
        "sortOrder": "ascending"
    }

    response = requests.get( url, headers=headers, params=params )
    response.raise_for_status()
    
    data = response.json()
    dict1 = data[ 'domains' ]

    for i in dict1:
        #print( i )
        #print( "\n" )
        for key, value in i.items():
            #print( key )
            if value == ffprojectname:
                uniqueID = i[ 'id' ]
                print( ffprojectname, "unique id is:", uniqueID )
                print( "Beginning API calls to FastFuels . . ." )
                postTopo()

def postTopo():
    print( "Requesting a topography grid to be created for", ffprojectname )
    topourl = "https://api.fastfuels.silvxlabs.com/v1/domains/" + uniqueID + "/grids/topography"

    json = { "attributes": ["elevation"],
             "elevation": {
                 "source": "3DEP",
                 "interpolationMethod": "cubic"
             }
           }
    response = requests.post( topourl, headers=headers, json=json )
    response.raise_for_status()
    if response.status_code == 201:
        print( 'Topography grid requested.  Monitoring status for completion.' )
        #start polling fnc
        poll_process_status( topourl, 10, 600, 'TopoGrid' )
    else:
        print( response )
        #need to add some language if not a 201 response. . . .

def postMakeTopoImageExport():
    print( "Requesting preparation of the topography grid export in geotiff format.")
    getexporturl = "https://api.fastfuels.silvxlabs.com/v1/domains/" + uniqueID + "/grids/topography/exports/geotiff"

    response = requests.post( getexporturl, headers=headers )
    response.raise_for_status()

    if response.status_code == 201:
        print( "Geotiff export request submitted.  Monitoring status for completion." )
        poll_process_status( getexporturl, 10, 600, "TopoGeotiffExport" )
    else:
        print( response )
        #need to add some language if not a 201 response. . . .

def downloadFile( fileUrl, filename ):
    print( f"Attempting to download { filename } ")
    try:
        downloadUrl = fileUrl
        response = requests.get( downloadUrl, stream=True )
        response.raise_for_status()
        with open( filename, 'wb' ) as f:
            for chunk in response.iter_content( chunk_size=8192 ):
                if chunk:
                    f.write( chunk )
        print( f"Downloaded { filename } to your working folder." )

    except requests.exceptions.RequestException as e:
        print( f"Dowload failed: { e }" )

def postCreateRoadFeature():
    print( "Requesting preparation of the Road Feature for better fuels." )
    roadurl = "https://api.fastfuels.silvxlabs.com/v1/domains/" + uniqueID + "/features/road"
    json = {
        "sources": [ "OSM" ]
    }
    response = requests.post( roadurl, headers=headers, json=json )
    response.raise_for_status()
    #data = response.json()
    if response.status_code == 201:
        print( 'Road feature requested.  Monitoring status for completion.' )
        poll_process_status( roadurl, 10, 600, 'RoadFeature' )
    else:
        print( response )
        #need to add some language if not a 201 response. . . .

def postCreateWaterFeature():
    print( "Requesting preparation of the Water Feature for better fuels." )
    waterurl = "https://api.fastfuels.silvxlabs.com/v1/domains/" + uniqueID + "/features/water"
    json = {
        "sources": [ "OSM" ]
    }

    response = requests.post( waterurl, headers=headers, json=json )
    response.raise_for_status()
    if response.status_code == 201:
        print( 'Water feature requested.  Monitoring status for completion.' )
        poll_process_status( waterurl, 10, 600, 'WaterFeature' )
    else:
        print( response )
        #need to add some language if not a 201 response. . . .

def postCreateTreeInventory():
    print( "Requesting creation of the tree inventory." )
    treeurl = "https://api.fastfuels.silvxlabs.com/v1/domains/" + uniqueID + "/inventories/tree"
    json = {
        "sources": [ "TreeMap" ],
        "TreeMap": {
            "version": "2022"
        }
    }
    response = requests.post( treeurl, headers=headers, json=json )
    response.raise_for_status()
    if response.status_code == 201:
        print( 'Tree inventory requested.  Monitoring status for completion.' )
        poll_process_status( treeurl, 10, 600, 'TreeInventory' )
    else:
        print( response )
        #need to add some language if not a 201 response. . . .

def postMakeTreeInventoryExport():
    print( "Requesting preparation of the tree inventory export in .csv format." )
    treeexporturl = "https://api.fastfuels.silvxlabs.com/v1/domains/" + uniqueID + "/inventories/tree/exports/csv"
    response = requests.post( treeexporturl, headers=headers )
    response.raise_for_status()
    if response.status_code == 201:
        print( "Treelist CSV export request submitted.  Monitoring status for completion." )
        poll_process_status( treeexporturl, 10, 600, "TreeInventoryExport" )
    else:
        print( response )
        #need to add some language if not a 201 response. . . .

def getTopoMetaData():
    print( "Getting topography metadata and writing file." )
    global nX
    global nY
    topoATTRurl = "https://api.fastfuels.silvxlabs.com/v1/domains/" + uniqueID + "/grids/topography/attributes"
    response = requests.get( topoATTRurl, headers=headers )
    response.raise_for_status()
    responsejson = response.json()
    #Set the variables so we can use it for the NAIP and treelist functions later.
    nX = responsejson[ 'shape' ][ 1 ]
    print( "NX=", nX )
    nY = responsejson[ 'shape' ][ 0 ]
    print( "NY=", nY )
    with open( 'topo_metadata.json', 'w' ) as f:
        json.dump( responsejson, f, indent=4 )
    print( "Topo metadata json file written to folder and includes NX and NY values, for future reference." )
    getDomain()

def getDomain():
    print( "Getting domain attributes for NAIP request.")
    domainurl = "https://api.fastfuels.silvxlabs.com/v1/domains/" + uniqueID
    response = requests.get( domainurl, headers=headers )
    response.raise_for_status()
    responsejson = response.json()
    #how to get crs
    #print( responsejson[ 'crs' ][ 'properties' ][ 'name' ] )
    crstext = responsejson[ 'crs' ][ 'properties' ][ 'name' ].split( ':' )
    crsNumber = str( crstext[ 1 ] )
    coords = responsejson[ 'features' ][ 0 ][ 'geometry' ][ 'coordinates' ][ 0 ]
    #print( coords )
    latValues = []
    lonValues = []
    for set in coords:
        x = set[ 0 ]
        y = set[ 1 ]
        lonValues.append( x )#Easting
        latValues.append( y )#Northing
    getNaip( min( lonValues ), min( latValues ), max( lonValues ), max( latValues ), crsNumber, nX, nY )

def getNaip( minLon, minLat, maxLon, maxLat, crs, nx, ny ):
    print( "Requesting custom NAIP imagery matching the domain." )
    IMAGE_SERVER = (
        "https://imagery.nationalmap.gov/arcgis/rest/services/"
        "USGSNAIPPlus/ImageServer/exportImage"
    )
    bbox = ( minLon, minLat, maxLon, maxLat )
    imageSize = str( nx ) + "," + str( ny )
    params = {
        "bbox": ",".join( map( str, bbox ) ),
        "bboxSR": crs,          # CRS of bbox
        "imageSR": crs,         # CRS of output
        "size": imageSize,     # control output resolution
        "format": "png",
        "pixelType": "U8",
        "interpolation": "RSP_BilinearInterpolation",
        "f": "image"
    }
    resp = requests.get( IMAGE_SERVER, params=params, timeout=120 )
    resp.raise_for_status()
    with open( "naip_5070_clip.png", "wb" ) as f:
        f.write( resp.content )
    print( "NAIP imagery downloaded to your folder in EPSG:5070" )
    reviseTreelist()

#Helper function for mapping each tree lat/lon to x/y in 3D space that matches domain.
def num_to_range( num, inMin, inMax, outMin, outMax ):
    return float( outMin + ( ( num - inMin ) / ( inMax - inMin ) * ( outMax - outMin ) ) )

def reviseTreelist():
    print( "Creating adjusted treelist." )
    treeCount = 0
    try:
        with open( "treelist.csv", mode='r', newline='' ) as inputcsv:
            reader = csv.reader( inputcsv )
            treelist_rows = list( reader )
            headers = treelist_rows[ 0 ]
            datarows = treelist_rows[ 1: ]
            lonList = []
            latList = []
            #print( headers )
            #print( datarows[8] )

        for i in datarows:
            #print( i[8] )
            lonList.append( i[ 8 ] )
            latList.append( i[ 9 ] ) 

        minX = min( lonList )
        maxX = max( lonList )
        minY = min( latList )
        maxY = max( latList )
        #print( minX, maxX, minY, maxY )

        i = 0
        for row in datarows:
            adjustedX = num_to_range( float( row[ 8 ] ), float( minX ), float( maxX ), float( -nX ), float( nX ) )
            adjustedY = num_to_range( float( row[ 9 ] ), float( minY ), float( maxY ), float( -nY ), float( nY ) )
            treeCount = treeCount + 1
            #Handle the cases (usually status 2 trees/dead) where CR is null
            cr = row[ 7 ]
            #print( cr )
            if cr == '':
                cr = 0
            datarows[ i ] = [ row[0], row[1], row[2], row[3], row[4], row[5], row[6], cr, adjustedX, adjustedY, row[10], row[11] ]
            i = i + 1
        
        with open( "newTreelist.csv", mode='w', newline='' ) as outputcsv:
            writer = csv.writer( outputcsv )
            writer.writerow( headers)
            for row in datarows:
                writer.writerow( row )
            print( "Processed", treeCount, "tree locations to the newTreelist.csv file." )

        getElevData()

    except FileNotFoundError:
        print( f"The file treelist.csv was not found." )
    except Exception as e:
        print( f"An error occurred: { e }" )

def getElevData():
    print( "Retreiving elevation data for 3D vertical scale if using geotiff to displace." )
    topoEurl = "https://api.fastfuels.silvxlabs.com/v1/domains/" + uniqueID + "/grids/topography/elevation/data"
    
    params = {
        "format": "json"
    }
    response = requests.get( topoEurl, headers=headers, params=params )
    response.raise_for_status()
    responsejson = response.json()
    elevationList = responsejson[ 'data' ]
    minElev = min( elevationList )
    maxElev = max( elevationList )
    rangeElev = maxElev - minElev

    print( f"Min: { minElev } Max: { maxElev } Range: { rangeElev }")
    print( f"WRITE DOWN OR SAVE: { rangeElev } for use in your Blender file." )
    finishScript()

def finishScript():
    scriptEnd = time.time()
    timeElapsed = scriptEnd - scriptStart
    print( f"All processes finished in { timeElapsed } seconds." )

def poll_process_status( url, interval=30, timeout=600, pollName='' ):
    #This is currently a static, set interval poll, and needs to be improved to an exponential poll once the results and "normal" timeframes are determined.
    """
    Polls the URL at regular intervals to check the status of a process. (process status = completed)
    It also helps control the sequence of the calls for the entire process.

    Args:
        url (str): The endpoint to send GET requests to.
        interval (int): Time in seconds to wait between requests.
        timeout (int): Maximum time in seconds to continue polling.
        pollName (str): A descriptive name of the process being polled for completion, which also triggers next call based on name
    """
    start_time = time.time()
    end_time = start_time + timeout

    while time.time() < end_time:
        try:
            # Set a timeout for the individual request to prevent it from hanging
            response = requests.get( url, headers=headers, timeout=10 )
            response.raise_for_status()
            if response.status_code == 404:
                break
            status_data = response.json()
            process_status = status_data[ 'status' ]
            print( f"Current status of: { pollName } is { process_status } (elapsed time: { int( time.time() - start_time ) }s)" )
            if process_status == 'completed':
                print( pollName, "complete!" )
                if pollName == "TopoGrid":
                    postMakeTopoImageExport()
                elif pollName == "TopoGeotiffExport":
                    #Consider naming the geotiff to the project name?
                    downloadFile( status_data[ 'signedUrl' ], 'topo.geotiff' )
                    postCreateRoadFeature()
                elif pollName == "RoadFeature":
                    postCreateWaterFeature()
                elif pollName == "WaterFeature":
                    postCreateTreeInventory()
                elif pollName == "TreeInventory":
                    postMakeTreeInventoryExport()
                elif pollName == "TreeInventoryExport":
                    downloadFile( status_data[ 'signedUrl' ], 'treelist.csv' )
                    getTopoMetaData()
                break

        except requests.exceptions.Timeout:
            print( "Request timed out. Retrying..." )
        except requests.exceptions.RequestException as e:
            print( f"An error occurred: { e }" )
        
        # Wait for the specified interval before the next request
        time.sleep( interval )
    else:
        print( "Polling timed out. Process status unknown or not complete within the time limit." )

getProjectID()