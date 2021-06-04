from satpy import Scene, find_files_and_readers
from satpy.dataset import DataQuery, DataID
from datetime import datetime
from os.path import dirname
from shapely import wkt
from pyproj import Proj, itransform
from pyresample.geometry import AreaDefinition, create_area_def
from eoian.utils.resample import Resample


def main(input_file: str, area_wkt: str) -> "Dataset":
    files = find_files_and_readers(base_dir=dirname(input_file), reader='msi_safe')
    scn = Scene(filenames=files)
    scn.load(['B04', 'B08'])
    # area = wkt.loads(area_wkt)
    # bs = area.bounds

    # proj_in = Proj(init="epsg:4326")
    # proj_out = Proj(init="epsg:29902")
    # pll, pur = list(itransform(proj_in, proj_out, [bs[0:2], bs[2:4]], always_xy=True))
    # xy_bbox = list(pll)
    # xy_bbox.extend(list(pur))
    #
    # proj_string = "+proj=merc +lat_ts=56.5 +ellps=GRS80"
    # target_area_def = create_area_def(area_id, proj_string, shape=shape,
    #                                                 area_extent=area_extent)
    #
    # Resample(scn[], self.area_id, self.proj_string, self.shape, self.area_extent).dataset
    #
    # scn.resample("epsg:4326")
    # width = 425
    # height = 425
    # projection = '+init=EPSG:29902'
    # area_extent = (-5326849.0625, -5326849.0625, 5326849.0625, 5326849.0625)
    # AreaDefinition(area_id, description, proj_id, projection, width, height, area_extent)
    # sub_scn = scn.crop(xy_bbox=xy_bbox)
    # scn.load(['B04', 'B08'])
    # area = wkt.loads(area_wkt)
    ndvi = (scn['B08'] - scn['B04']) / (scn['B08'] + scn['B04'])
    return ndvi.compute().to_dataset(name='ndvi')