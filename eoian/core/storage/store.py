import datetime
import functools
import tempfile
from os import makedirs, remove
from os.path import dirname, join
import numpy as np
import xarray as xr
import rioxarray
from pyresample import kd_tree, geometry
from zarr.errors import GroupNotFoundError
from .. utils.resample import Resample
from .. settings import configuration
from .store_objects import ReadWriteData


class GeoTiffWriter:

    def __init__(self, store, dataset, file_path):
        self.store = store
        self.dataset = dataset
        self.full_path = None
        self.file_path = file_path
        self.to_store()

    def write(self, full_path):
        self.dataset.rio.to_raster(full_path)

    def to_store(self):
        with tempfile.TemporaryDirectory() as tempdir:
            full_path = join(tempdir, self.file_path)
            makedirs(dirname(full_path))
            self.write(full_path)
            self.store.upload_file(full_path, self.file_path)
            # TODO: self.to_store()


class Store:

    def __init__(self, platform, store, product_directory):
        self.platform = platform
        self.top_level_directory = product_directory
        self.store = store
        self._dataset = None
        self.area_id = None
        self.proj_string = None
        self.shape = None
        self.area_extent = None

    @staticmethod
    def expand_and_add_coord(ds, value, dim):
        ds = ds.expand_dims(dim=dim)
        ds[dim] = [value]
        ds = ds.assign_coords({dim: [value]})
        return ds

    def set_area_info(self):
        if not (self.area_id or self.proj_string):
            datacube = self.read_zarr()
            if datacube:
                self.area_id = datacube.attrs['area_id']
                self.proj_string = datacube.attrs['proj_string']
                self.shape = datacube.attrs['shape']
                self.area_extent = datacube.attrs['area_extent']

    def resample(self):
        self.set_area_info()
        self._dataset = Resample(self._dataset, self.area_id, self.proj_string, self.shape, self.area_extent).dataset
        return self

    def add_dims(self, info):
        start_time = datetime.datetime.strptime(self._dataset.start_date, '%d-%b-%Y %H:%M:%S.%f')
        self._dataset = self.expand_and_add_coord(self._dataset, start_time, 'time')
        self._dataset[r'relativeOrbitNumber'] = xr.DataArray(data=[info[r'relativeOrbitNumber']], dims=['time'])
        self._dataset['platformSerialIdentifier'] = xr.DataArray(data=[info['platformSerialIdentifier']], dims=['time'])
        self._dataset['title'] = xr.DataArray(data=[info['title']], dims=['time'])
        return self

    def to_zarr(self):
        ds_store = self.store.read()
        print(f"{ds_store=}")
        print(f"{self._dataset=}")
        try:
            self.store.to_zarr(self._dataset)
        except:
            raise
        return self

    def read_zarr(self):
        return self.store.read()

    def to_tiff(self, product_path):
        product_path = join(self.top_level_directory, product_path)
        GeoTiffWriter(self.store, self._dataset, product_path)
        return self

    @property
    def dataset(self):
        return self._dataset

    @dataset.setter
    def dataset(self, dataset):
        self._dataset = dataset

    def __repr__(self):
        return repr(self.store)


class Stores:

    def __init__(self):
        self.platform = configuration()

    @functools.lru_cache
    def postprocess(self, product_name):
        store = ReadWriteData(self.platform, product_name)
        return Store(self.platform, store, product_name)
