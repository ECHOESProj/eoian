"Name:"

"Description:"

"Minimum Requirements:",

"Inputs:"

"Outputs:",

"Author:",

"Created:",

import os
import sqlite3

import numpy as np
import pandas as pd
import rasterio
from affine import Affine
from pyproj import Proj, transform
from rasterio.plot import show

spatialite_location = r"C:\Users\ckelly.COMPASSINFORMAT\tools\mod_spatialite-NG-win-amd64;"

os.environ["PATH"] = (
        spatialite_location
        + os.environ["PATH"]
)


def geo_process(db_filename, filename):
    with rasterio.read(filename) as r:
        T0 = r.transform  # upper-left pixel corner affine transform
        p1 = Proj(r.crs)  # pixel crs projection
        A = r.read()  # pixel values
        show(r)
        print("A:", A)
    # for i in A[0][0]:
    # print(i)
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
    p2 = Proj(proj='latlong', datum='WGS84')
    longs, lats = transform(p1, p2, eastings, northings)

    group = []
    # lats, lngs and values zipped together for sequential looping
    for f, b, c in zip(longs, lats, A[0]):
        # print(f, b, c)
        for j, (d, k, t) in enumerate(zip(f, b, c)):
            # print(j,d,k,t)
            a = j, d, k, t
            group.append(a)
            # If the output needs to be subsetted
            # if j % 1000 == 0:
            # a = j,d,k,t
            # group.append(a)

    # Dataframe is created of the array produced in the loop
    e_dataframe = pd.DataFrame(group)
    # Columns are renamed
    e_dataframe.columns = ['No', 'lat', 'lng', 'val']
    print(e_dataframe)
    # e_dataframe.to_csv(r"D:\Projects\Active\Intereg_Echeos\RF_TESTfile.csv")
    print("Dataset has been converted to Dataframe")

    with sqlite3.connect(db_filename) as conn:

        conn.row_factory = sqlite3.Row  # results can then be used liked dicts
        conn.enable_load_extension(True)
        # load spatialite extension
        conn.execute('SELECT load_extension("mod_spatialite")')
        curs = conn.cursor()

        e_dataframe.to_sql('RF_TEST_habitat_classification', conn, if_exists='replace', index=False)
        sql = "SELECT AddGeometryColumn('RF_TEST_habitat_classification', 'geometry', 4326, 'POINT', 'XY')"
        sql1 = "UPDATE RF_TEST_habitat_classification SET Geometry=MakePoint(lat, lng, 4326)"

        curs.execute(sql)
        curs.execute(sql1)
        conn.commit()
        print("Data has been exported to SQLite database")


def main():
    db_filename = r"D:/Projects/Active/Intereg_Echeos/Echoes_processing_db.sqlite"

    filename = r"D:\\Projects\\Active\\Intereg_Echeos\\RF_TEST\\RF_TEST_subset2.tif"

    geo_process(db_filename, filename)


if __name__ == "__main__":
    # only run this if this is the start up script and not imported
    main()
    print("Done!")
