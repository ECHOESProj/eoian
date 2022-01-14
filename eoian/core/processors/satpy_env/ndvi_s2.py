#  Copyright (c) 2022.
#  The ECHOES Project (https://echoesproj.eu/) / Compass Informatics

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
    xmin, ymin, xmax, ymax = area.bounds
    (nxmin, nxmax), (nymin, nymax) = reproject(4326, out_proj_espg_num, (xmin, xmax), (ymin, ymax))
    return nxmin, nymin, nxmax, nymax


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
    s = scn.resample(ad)

    ndvi = (s['B08'] - s['B04']) / (s['B08'] + s['B04'])
    s['ndvi'] = ndvi
    s['ndvi'].attrs['area'] = s['B08'].attrs['area']
    del s['B04']
    del s['B08']
    return s
