''' 
Name: GeoServer Vector Data Automation"

Description: This script connects to any Geoserver instance. It will first look for a workspace, if none found a new one will be created. 
             It will then look for a store, if the store is no present a new one will be created using the PostGIS connection. It will then
             publish a layer within this store."

Minimum Requirements: Geoserver login details, gsconfig module

Inputs: Geoserver connection details, Database information

"Outputs: Publish WMS/WFS layers",

"Author: Caoimhin Kelly",

"Created: 16/11/2020"

'''

#  Copyright (c) 2022.
#  The ECHOES Project (https://echoesproj.eu/) / Compass Informatics

# Declare required modules
from geoserver.catalog import Catalog, FailedRequestError
from geoserver.support import JDBCVirtualTable, JDBCVirtualTableGeometry, JDBCVirtualTableParam
import psycopg2
import sqlalchemy as db
import rasterio
from rasterio.io import MemoryFile
from osgeo import gdal
import numpy
from PIL import Image
from rasterio.transform import from_origin
import os, stat
import pygresql as pg

def raster_process():
    
    outfile = 'D:\Projects\Active\Intereg_Echeos\RemoteSensing\Images\temp.tiff'
    pg_table = 'subset_s2a_msil2a_20201022_ndvi'

    pg_hex = 'D:\Projects\Active\Intereg_Echeos\RemoteSensing\Images\temp.hex'
    os.mknod(pg_hex, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP)

    sql = "COPY (SELECT encode(ST_AsTIFF(ST_Union(" + pg_table + ".rast)), 'hex') FROM " + pg_table + ") TO '" + pg_hex + "'"
    conn = pg.connect('echoes', 'W19-PostGIS', 5432, None, None, 'postgres')
    
    conn.query(sql)

    cmd = 'xxd -p -r ' + pg_hex + ' > ' + outfile
    os.system(cmd)


# Publication definition
def publication_process(Workspace,store,layer):
    
    # Geoserver connection is established.
    cat = Catalog("http://192.168.0.146:8080/geoserver/rest/", username="admin", password="geoserver")
    print("GeoServer Connected")

    # Workspace name is searched, if none is returned a new workspace is created.
    if cat.get_workspace(Workspace) == None:
       ws = cat.create_workspace(Workspace, 'http://example.com/wmstest')
       print("\n Could not find the required workspace, A new workspace has been created named:",ws)
    else:
       ws = cat.get_workspace(Workspace)
       print("\n Required workspace:",ws,"found")
    
    # Store is searched for within the workspace
    store = "ID"

    tds = cat.get_file_sys_io(store, ws)
    print(tds)
    cat.delete(tds)
    cat.reload()
    #cat.save(ft)
    # If the returned list of stores is empty a new store is created connecting to the PostGIS database. If returned the store is loaded.
    cat.create_coveragestore(name= store,
                         path='D:\Projects\Active\Intereg_Echeos\RemoteSensing\Sentinel-1\Ireland\Sen1_20201028\processed_output\GeoTIFF\Flooding_Estimation.TIF',
                         workspace=ws,
                         overwrite=True)

def main():

    # Define Workspace, store and the layer to be published
    Workspace = 'test'
    store = 'test1'
    layer = 'ireland_locat_authority'

    raster_process()

    # Call to the publication function
    #publication_process(Workspace,store,layer)
    
if __name__ == "__main__":
    # only run this if this is the start up script and not imported
    main()
    print ("Done!")