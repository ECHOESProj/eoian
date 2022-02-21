
import xarray as xr
from eoian.__main__ import *
from eo_io import configuration, ReadWriteData

config_s3 = configuration()
store = ReadWriteData(config_s3)


def test_processing():
    instrument = 'S2_MSI_L1C'
    processing_module = 'ndvi_s2'
    area_wkt = "POLYGON ((-6.485367 52.328206, -6.326752 52.328206, -6.326752 52.416241, -6.485367 52.416241, -6.485367 52.328206))"
    start = '2021-07-14'
    stop = '2021-07-19'
    cloud_cover = 90
    pc = ProcessingChain(instrument, processor(processing_module), area_wkt, start, stop, cloud_cover=cloud_cover)
    assert isinstance(store.read_zarr(pc.file_paths_zarr[0]), xr.Dataset)
