"Name:"

"Description:"

"Minimum Requirements:",

"Inputs:"

"Outputs:",

"Author:",

"Created:",

import os 
from osgeo import gdal
import sqlite3
import matplotlib.pyplot as plt
import rasterio
import numpy as np
from affine import Affine
from pyproj import Proj, transform
import pandas as pd
import geopandas as gpd
from geopandas.tools import sjoin
from rasterio.plot import show
from rasterio.plot import show_hist
import shapely.speedups

shapely.speedups.enable()

spatialite_location = r"C:\Users\ckelly.COMPASSINFORMAT\tools\mod_spatialite-NG-win-amd64;"

os.environ["PATH"] = (
            spatialite_location
            + os.environ["PATH"]
        )
def retrieve_sites(db_filename,sql):
    
    with sqlite3.connect(db_filename)as conn:

        conn.row_factory = sqlite3.Row  # results can then be used liked dicts
        conn.enable_load_extension(True)
        # load spatialite extension
        conn.execute('SELECT load_extension("mod_spatialite")')
        curs = conn.cursor()

        site_gdf = gpd.GeoDataFrame.from_postgis(sql, conn, geom_col='geom')
       
    return site_gdf

def geo_process(db_filename,filename):

    #ds = gdal.Open(filename).ReadAsArray()

    #im = plt.imshow(ds)
    
    with rasterio.read(filename) as r:
        T0 = r.transform  # upper-left pixel corner affine transform
        p1 = Proj(r.crs)
        A = r.read()  # pixel values
        show(r)

    #for i in A[0][0]:
        #print(i)
    print(len(A))
    # All rows and columns
    cols, rows = np.meshgrid(np.arange(A.shape[2]), np.arange(A.shape[1]))

    # Get affine transform for pixel centres
    T1 = T0 * Affine.translation(0.5, 0.5)
    # Function to convert pixel row/column index (from 0) to easting/northing at centre
    rc2en = lambda r, c: (c, r) * T1

    # All eastings and northings (there is probably a faster way to do this)
    eastings, northings = np.vectorize(rc2en, otypes=[np.float, np.float])(rows, cols)

    # Project all longitudes, latitudes
    p2 = Proj(proj='latlong',datum='WGS84')
    longs, lats = transform(p1, p2, eastings, northings)
    
    group = []
    for f, b, c in zip(longs, lats, A[0]):
        #print(f, b, c)
        for j,(d,k,t) in enumerate(zip(f,b, c)):
            #print(j,d,k,t)
            a = j,d,k,t
            group.append(a)
            #if j % 1000 == 0:
                #a = j,d,k,t
                #group.append(a)
    e_dataframe = pd.DataFrame(group)
    e_dataframe.columns = ['No', 'lat', 'lng', 'val']
    
    geo_dataframe = gpd.GeoDataFrame(
    e_dataframe, geometry=gpd.points_from_xy(e_dataframe.lng, e_dataframe.lat))
    geo_dataframe = geo_dataframe.set_crs(epsg=4326)
    print("geo_dataframe.crs:", geo_dataframe.crs)
    
    sql = 'select id,Hex(ST_AsBinary(geom)) as geom from test_sites'
    site_gdf = retrieve_sites(db_filename,sql)
    site_gdf = site_gdf.set_crs(epsg=4326)
    print("site_gdf.crs:", site_gdf.crs)

    #res_intersection = gpd.sjoin(geo_dataframe, site_gdf, op='within')
    res_intersection = gpd.clip(geo_dataframe, site_gdf)
    print(res_intersection)
    


def main():

    db_filename = r"D:/Projects/Active/Intereg_Echeos/Echoes_processing_db.sqlite"

    filename = r"D:\\Projects\\Active\\Intereg_Echeos\\RF_TEST\\RF_TEST_subset.tif"

    geo_process(db_filename,filename)

if __name__ == "__main__":
    # only run this if this is the start up script and not imported
    main()
    print ("Done!")
