#  Copyright (c) 2022.
#  The ECHOES Project (https://echoesproj.eu/) / Compass Informatics

import abc
import datetime
import functools
import json
import numpy as np
import os
import rioxarray
import tempfile
from satpy.scene import Scene
import xarray as xr
from os import makedirs, remove
from os.path import dirname, join
from pyresample import kd_tree, geometry
from zarr.errors import GroupNotFoundError

from .store_objects import ReadWriteData
from ..settings import configuration
from ..utils.resample import Resample


class BaseWriter(abc.ABC):

    def __init__(self, store, data, top_level_directory, product_identifier, extension):
        self.store = store
        self.data = data
        file_path = self._product_path(product_identifier, extension)
        self.to_store(join(top_level_directory, file_path))

    @staticmethod
    def _product_path(product_identifier, extension):
        product_path = '/'.join(product_identifier.split('/')[2:])
        return os.path.splitext(product_path)[0] + extension

    @abc.abstractmethod
    def write(self, full_path):
        pass

    def to_store(self, file_path):
        with tempfile.TemporaryDirectory() as tempdir:
            full_path = join(tempdir, file_path)
            makedirs(dirname(full_path))
            self.write(full_path)
            self.store.upload_file(full_path, file_path)


class GeoTiffWriter(BaseWriter):

    def write(self, full_path):
        self.data.rio.to_raster(full_path)


class SceneGeoTiffWriter(BaseWriter):

    def write(self, full_path):
        name = self.data.keys()[0]
        self.data.save_datasets(datasets=[name, ], filename=full_path, writer='geotiff', include_scale_offset=True,
                                dtype=np.float32)


class MetaDataWriter(BaseWriter):

    def write(self, full_path):
        with open(full_path, 'w') as f:
            json.dump(self.data, f)


class Store:

    def __init__(self, platform, store, product_directory):
        self.platform = platform
        self.top_level_directory = product_directory
        self.store = store
        self._dataset = None
        self._info = None
        self.area_id = None
        self.proj_string = None
        self.shape = None
        self.area_extent = None
        self.scene = None

    @staticmethod
    def _expand_and_add_coord(ds, value, dim):
        ds = ds.expand_dims(dim=dim)
        ds[dim] = [value]
        ds = ds.assign_coords({dim: [value]})
        return ds

    def _set_area_info(self):
        if not (self.area_id or self.proj_string):
            datacube = self.read_zarr()
            if datacube:
                self.area_id = datacube.attrs['area_id']
                self.proj_string = datacube.attrs['proj_string']
                self.shape = datacube.attrs['shape']
                self.area_extent = datacube.attrs['area_extent']

    def resample(self):
        self._set_area_info()
        self._dataset = Resample(self._dataset, self.area_id, self.proj_string, self.shape, self.area_extent).dataset
        return self

    def add_attributes_to_dataset(self):
        start_time = datetime.datetime.strptime(self._dataset.start_date, '%d-%b-%Y %H:%M:%S.%f')
        self._dataset = self._expand_and_add_coord(self._dataset, start_time, 'time')
        self._dataset[r'relativeOrbitNumber'] = xr.DataArray(data=[self._info[r'relativeOrbitNumber']], dims=['time'])
        self._dataset['platformSerialIdentifier'] = xr.DataArray(data=[self._info['platformSerialIdentifier']],
                                                                 dims=['time'])
        self._dataset['title'] = xr.DataArray(data=[self._info['title']], dims=['time'])
        return self

    def read_zarr(self):
        return self.store.read()

    def to_zarr(self):
        ds_store = self.store.read()
        try:
            self.store.to_zarr(self._dataset)
        except:
            raise
        return self

    def to_tiff(self):
        GeoTiffWriter(self.store, self._dataset, self.top_level_directory, self._info['productIdentifier'], '.tif')
        return self

    def metadata_to_json(self):
        MetaDataWriter(self.store, self._info, self.top_level_directory, self._info['productIdentifier'], '.json')
        return self

    @property
    def dataset(self):
        return self._dataset

    @dataset.setter
    def dataset(self, dataset):
        self._dataset = dataset

    @property
    def info(self):
        return self._info

    @info.setter
    def info(self, info):
        self._info = info

    def __repr__(self):
        return repr(self.store)


class StoreScene(Store):

    @Store.dataset.setter
    def dataset(self, dataset):
        self.scene = dataset
        self._dataset = dataset[dataset.keys()[0]]

    def to_tiff(self):
        SceneGeoTiffWriter(self.store, self.scene, self.top_level_directory, self._info['productIdentifier'], '.tif')
        return self


class Stores:

    def __init__(self):
        self.config = configuration()

    def get_store(self, product_name, dataset, info):
        store = self._get_store(product_name, dataset)
        store.dataset = dataset
        store.info = info
        return store

    @functools.lru_cache
    def _get_store(self, product_name, dataset):
        store = ReadWriteData(self.config, product_name)
        if isinstance(dataset, Scene):
            store_cls = StoreScene
        else:
            store_cls = Store
        return store_cls(self.config, store, product_name)
