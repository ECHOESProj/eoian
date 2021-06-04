from satpy import Scene, find_files_and_readers
from satpy.dataset import DataQuery, DataID
from pyproj import Proj
from datetime import datetime
from os.path import dirname


def main(input_file: str, area_wkt: str) -> "Dataset":
    files = find_files_and_readers(base_dir=dirname(input_file), reader='sar-c_safe')
    scn = Scene(filenames=files)
    hh_id = DataQuery(name="measurement", polarization="vh")
    scn.load([hh_id, 'latitude'])
    return scn[hh_id]