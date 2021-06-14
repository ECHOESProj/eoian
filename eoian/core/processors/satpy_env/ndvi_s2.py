from satpy import Scene, find_files_and_readers
from satpy.dataset import DataQuery, DataID
from datetime import datetime
from os.path import dirname
from shapely import wkt
from pyproj import Proj, itransform
from pyresample.geometry import AreaDefinition, create_area_def
from ... utils.resample import Resample


# from satpy.utils import debug_on
# debug_on()


def get_bounds(area, out_proj_espg_num):
    proj_in = Proj(init="epsg:4326")
    proj_out = Proj(init="epsg:" + str(out_proj_espg_num))
    bs = area.bounds
    pll, pur = list(itransform(proj_in, proj_out, [bs[0:2], bs[2:4]], always_xy=True))
    xy_bbox = list(pll)
    xy_bbox.extend(list(pur))
    return xy_bbox


def main(input_file: str, area_wkt: str) -> "Dataset":
    files = find_files_and_readers(base_dir=dirname(input_file), reader='msi_safe')
    scn = Scene(filenames=files)
    scn.load(['B04', 'B08'])
    area = wkt.loads(area_wkt)
    epsg = scn['B04'].area.crs.to_epsg()
    xy_bbox = get_bounds(area, epsg)
    print(xy_bbox)
    print('Cropping')
    scn = scn.crop(xy_bbox=xy_bbox)
    print('Cropping finished')
    ndvi = (scn['B08'] - scn['B04']) / (scn['B08'] + scn['B04'])
    return ndvi.compute().to_dataset(name='ndvi')