"Name:"

"Description:"

"Minimum Requirements:",

"Inputs:"

"Outputs:",

"Author:",

"Created:",

import os

import geopandas as gpd
import matplotlib.pyplot as plt
import rasterio
import rasterio.mask
import rioxarray as rxr
from pyproj import Proj
from rasterio.mask import mask
from rasterio.plot import show
from shapely.geometry import mapping

spatialite_location = r"C:\Users\ckelly.COMPASSINFORMAT\tools\mod_spatialite-NG-win-amd64;"

os.environ["PATH"] = (
        spatialite_location
        + os.environ["PATH"]
)


def geo_process(db_filename, filename):
    fp = r"D:\Projects\Active\Intereg_Echeos\download(14)\layers\POLYGON.shp"

    sdf = gpd.read_file(fp)

    lidar_chm_im = rxr.open_rasterio(filename, masked=True).squeeze()

    print('sdf crs: ', sdf.crs)
    print('lidar crs: ', lidar_chm_im.rio.crs)

    f, ax = plt.subplots()
    lidar_chm_im.plot.imshow(ax=ax)

    sdf.plot(ax=ax, alpha=.8)
    ax.set(title="Raster Layer with Shapefile Overlayed")

    ax.set_axis_off()
    plt.show()

    lidar_clipped = lidar_chm_im.rio.clip(sdf.geometry.apply(mapping), sdf.crs)

    path_to_tif_file = os.path.join("D:\Projects\Active\Intereg_Echeos\Snadbox\lidar_chm_cropped.tif")
    with rasterio.open(lidar_clipped) as r:
        A = lidar_clipped.read()  # pixel values
        show(lidar_clipped)
        print("A:", A)

    lidar_clipped.rio.to_raster(path_to_tif_file)


def pixels2points():
    fp = r"D:\\Projects\\Active\\Intereg_Echeos\\RF_TEST\\POLYGON2.shp"

    sdf = gpd.read_file(fp)

    raster_path = "D:\\Projects\\Active\\Intereg_Echeos\\RF_TEST\\clipped2.tif"

    # Reading tif file
    raster = rasterio.open(raster_path)
    print(raster.read())
    # copy of raster metadata
    out_meta = raster.meta.copy()

    # clipping raster using a polygon
    out_window, out_transform = mask(raster, sdf.geometry.apply(mapping), all_touched=True, crop=True)

    print(out_window.read())
    # Using 'out_meta' 'out_window' and 'out_transform' we can obtain window dimensions
    # and position of top left cell of the window => x, y, width, height

    # Reading original values using same size window as array produced by clipping with polygon
    # window_orig = raster.read(1, window=from_bounds(left, bottom, right, top, src.transform))

    # Swapping values different to NoData with their average value.
    # If NoData then use original values
    # window_avg = (np.where(out_window!=-1, int(round(avg,0)), window_orig))

    # Writing back to raster
    # with rasterio.open(raster_path, "r+", **out_meta) as dest:
    # dest.write(window_avg, window=Window(x, y, width, height))

    # img = georaster.SingleBandRaster("D:\Projects\Active\Intereg_Echeos\RF_TEST\qgisclip.tif")
    # img = geoio.GeoImage("D:\Projects\Active\Intereg_Echeos\RF_TEST\RF_TEST_subset2)84_clip.tif")
    with rasterio.open("D:\\Projects\\Active\\Intereg_Echeos\\RF_TEST\\clipped2.tif") as r:
        T0 = r.transform  # upper-left pixel corner affine transform
        p1 = Proj(r.crs)
        A = r.read()  # pixel values
        show(r)
        print("A:", A, p1)


def main():
    db_filename = r"D:/Projects/Active/Intereg_Echeos/Echoes_processing_db.sqlite"

    filename = r"D:\\Projects\\Active\\Intereg_Echeos\\RF_TEST\\RF_TEST_20190615T141321.tif"

    # geo_process(db_filename,filename)

    pixels2points()


if __name__ == "__main__":
    # only run this if this is the start up script and not imported
    main()
    print("Done!")
