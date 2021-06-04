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
from rasterio.plot import show
from rasterio.plot import show_hist

spatialite_location = r"C:\Users\ckelly.COMPASSINFORMAT\tools\mod_spatialite-NG-win-amd64;"

os.environ["PATH"] = (
            spatialite_location
            + os.environ["PATH"]
        )

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
    e_dataframe = e_dataframe[e_dataframe['val'] < 300]
    print(e_dataframe)
    #e_dataframe.to_csv(r"D:\Projects\Active\Intereg_Echeos\RF_TESTfile.csv")  
    print("Dataset has been converted to Dataframe")
    
    with sqlite3.connect(db_filename)as conn:

        conn.row_factory = sqlite3.Row  # results can then be used liked dicts
        conn.enable_load_extension(True)
        # load spatialite extension
        conn.execute('SELECT load_extension("mod_spatialite")')
        curs = conn.cursor()

        e_dataframe.to_sql('RF_TEST_temp_file1', conn, if_exists='replace', index=False)
        sql = "SELECT AddGeometryColumn('RF_TEST_temp_file1', 'geometry', 4326, 'POINT', 'XY')"
        sql1 = "UPDATE RF_TEST_temp_file1 SET Geometry=MakePoint(lng, lat, 4326)"
        
        curs.execute(sql)
        curs.execute(sql1)
        conn.commit()
        print("Data has been exported to SQLite database")

def main():

    db_filename = r"D:/Projects/Active/Intereg_Echeos/Echoes_processing_db.sqlite"

    filename = r"D:\\Projects\\Active\\Intereg_Echeos\\RF_TEST\\RF_TEST_temperature_20140115.tif"

    geo_process(db_filename,filename)

if __name__ == "__main__":
    # only run this if this is the start up script and not imported
    main()
    print ("Done!")
