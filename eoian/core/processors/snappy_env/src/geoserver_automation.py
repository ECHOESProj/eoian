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
from geoserver.catalog import Catalog
from geoserver.support import JDBCVirtualTable, JDBCVirtualTableGeometry, JDBCVirtualTableParam

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
    tds = cat.get_file_sys_io(store, ws)

    # If the returned list of stores is empty a new store is created connecting to the PostGIS database. If returned the store is loaded.
    if not tds:
        print("\n There is no store with the name", store)
        ds = cat.create_datastore(store,ws)
        ds.connection_parameters.update(host='W19-PostGIS', port='5432', database='echoes', user='postgres', passwd='HuufDorf13!', dbtype='postgis', schema='external_datasets')
        cat.to_zarr(ds)
        print("\n A new store with the name", store, "has now been created")
    else:
        ds = cat.get_file_sys_io(store, ws)
        print('\n Store is has been found and is loaded.')
    
    # The specified layer is then ready to publish. 
    try:
        ft = cat.publish_featuretype(layer, ds, 'EPSG:4326', 'EPSG:4326')
        cat.to_zarr(ft)
        print("\n The",layer,"has been published")
    except:
        print("\n There is no layer with the name:", layer,"publishing has failed.")

def main():

    # Define Workspace, store and the layer to be published
    Workspace = 'test'
    store = 'test1'
    layer = 'ireland_locat_authority'

    # Call to the publication function
    publication_process(Workspace,store,layer)
    
if __name__ == "__main__":
    # only run this if this is the start up script and not imported
    main()
    print ("Done!")