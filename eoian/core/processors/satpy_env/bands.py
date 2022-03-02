#  Copyright (c) 2022.
#  The ECHOES Project (https://echoesproj.eu/) / Compass Informatics

from os.path import dirname
from satpy import Scene, find_files_and_readers
from shapely import wkt

from .utils import  get_bounds, area_def


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

    # s['ndvi'].attrs['area'] = s['B08'].attrs['area']
    del s['B04']
    del s['B08']
    return s
