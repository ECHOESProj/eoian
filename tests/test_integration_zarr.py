
import xarray as xr
from eoian.__main__ import *
from eo_io import configuration, ReadWriteData

config_s3 = configuration()
store = ReadWriteData(config_s3)


class ProcessingNotDoneError(AssertionError):
    pass


def test_processing():
    instrument = 'S2_MSI_L1C'
    processing_module = 'ndvi_s2'
    area_wkt = "POLYGON ((-6.485367 52.328206, -6.326752 52.328206, -6.326752 52.416241, -6.485367 52.416241, -6.485367 52.328206))"
    start = '2021-07-14'
    stop = '2021-07-19'
    cloud_cover = 90
    for d in ProcessingChain(instrument, processor(processing_module), area_wkt, start, stop, cloud_cover=cloud_cover):
        d.to_tiff()
        d.metadata_to_json()
        d.to_zarr()
        assert isinstance(store.read_zarr(d.file_path), xr.Dataset)
    else:
        raise ProcessingNotDoneError
