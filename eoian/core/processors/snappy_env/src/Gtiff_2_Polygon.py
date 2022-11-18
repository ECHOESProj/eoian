"Name:"

"Description:"

"Minimum Requirements:",

"Inputs:"

"Outputs:",

"Author:",

"Created:",

import os
import sqlite3

import geopandas as gpd
import shapely.speedups

shapely.speedups.enable()

spatialite_location = r"C:\Users\ckelly.COMPASSINFORMAT\tools\mod_spatialite-NG-win-amd64;"

os.environ["PATH"] = (
        spatialite_location
        + os.environ["PATH"]
)


def retrieve_sites(db_filename, sql):
    with sqlite3.connect(db_filename) as conn:
        conn.row_factory = sqlite3.Row  # results can then be used liked dicts
        conn.enable_load_extension(True)
        # load spatialite extension
        conn.execute('SELECT load_extension("mod_spatialite")')
        curs = conn.cursor()

        site_gdf = gpd.GeoDataFrame.from_postgis(sql, conn, geom_col='geom')

    return site_gdf


def subsetting(db_filename, filename):
    sql = 'select id,Hex(ST_AsBinary(geom)) as geom from test_sites'
    site_gdf = retrieve_sites(db_filename, sql)
    print("site_gdf.crs:", site_gdf.crs)

    sql = 'select No, val,Hex(ST_AsBinary(geom)) as geom  from pixel_points_subset'
    pixel_data = retrieve_sites(db_filename, sql)
    print("pixel_data:", pixel_data.crs)

    # res_intersection = gpd.sjoin(pixel_data, site_gdf, op='within')
    res_intersection = gpd.clip(pixel_data, site_gdf)
    print(res_intersection)


def main():
    db_filename = r"D:/Projects/Active/Intereg_Echeos/Echoes_processing_db.sqlite"

    filename = r"D:\\Projects\\Active\\Intereg_Echeos\\RF_TEST\\RF_TEST_subset.tif"

    subsetting(db_filename, filename)


if __name__ == "__main__":
    # only run this if this is the start up script and not imported
    main()
    print("Done!")
