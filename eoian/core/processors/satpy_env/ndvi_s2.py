import numpy as np
from datetime import datetime
from os.path import dirname
from pyproj import Proj, itransform
from pyresample.geometry import AreaDefinition, create_area_def
from satpy import Scene, find_files_and_readers
from satpy.dataset import DataQuery, DataID
from shapely import wkt
from xarray import DataArray

from ...utils import Resample, reproject


def get_bounds(area, out_proj_espg_num):
    bs = area.bounds
    xs, ys = (bs[0], bs[2]), (bs[1], bs[3])
    nx, ny = reproject(4326, out_proj_espg_num, xs, ys)
    xy_bbox = list(nx)
    xy_bbox.extend(list(ny))
    return xy_bbox


def area_def(area_extent, resolution):
    proj_dict = {'proj': 'longlat', 'datum': 'WGS84'}
    return create_area_def('ROI', proj_dict, units='degrees', area_extent=area_extent, resolution=resolution)


def main(input_file: str, area_wkt: str) -> "Dataset":
    files = find_files_and_readers(base_dir=dirname(input_file), reader='msi_safe')
    scn = Scene(filenames=files)
    scn.load(['B04', 'B08'])
    area = wkt.loads(area_wkt)

    epsg = scn['B04'].area.crs.to_epsg()
    xy_bbox = get_bounds(area, epsg)
    scn = scn.crop(xy_bbox=xy_bbox)

    extents = scn.finest_area().area_extent_ll
    ad = area_def(extents, 0.0001)
    s = scn.resample(ad)  # resampler='nearest'

    ndvi = (s['B08'] - s['B04']) / (s['B08'] + s['B04'])
    s['ndvi'] = ndvi
    s['ndvi'].attrs['area'] = s['B08'].attrs['area']
    del s['B04']
    del s['B08']
    # xs, ys = np.meshgrid(ndvi.x.values, ndvi.y.values)
    # lon1d, lat1d = reprojected(epsg, 4326, xs.ravel(), ys.ravel())
    # lons, lats = lon1d.reshape(ndvi.shape), lat1d.reshape(ndvi.shape)
    #
    # ndvi = ndvi.assign_coords(lon=DataArray(np.array(lons), dims=['y', 'x']))
    # ndvi = ndvi.assign_coords(lat=DataArray(np.array(lats), dims=['y', 'x']))
    return s
