#  Copyright (c) 2022.
#  The ECHOES Project (https://echoesproj.eu/) / Compass Informatics

from os.path import dirname
from satpy import Scene, find_files_and_readers, dataset
from shapely import wkt

from .utils import  get_bounds, area_def


def main(input_file: str, area_wkt: str) -> dataset:
    files = find_files_and_readers(base_dir=dirname(input_file), reader='msi_safe')
    scn = Scene(filenames=files)
    # bands_list = scn.available_dataset_names()
    bands_list = ['B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B08', 'B8A']
    scn.load(bands_list)
    area = wkt.loads(area_wkt)

    epsg = scn['B04'].area.crs.to_epsg()
    xy_bbox = get_bounds(area, epsg)
    scn = scn.crop(xy_bbox=xy_bbox)

    extents = scn.finest_area().area_extent_ll
    ad = area_def(extents, 0.0001)
    return scn.resample(ad)
