#  Copyright (c) 2022.
#  The ECHOES Project (https://echoesproj.eu/) / Compass Informatics

from datetime import datetime
from itertools import groupby
from os.path import join
import xarray as xr
import boto3
import s3fs
import zarr
from botocore.exceptions import ClientError
from zarr.errors import GroupNotFoundError


class ObjectStoreInterface:
    """Read and write to S3"""

    def __init__(self, platform):
        self.platform = platform
        self.bucketname = platform.bucket
        self.endpoints = {'external': self.platform.endpoint_url_local,
                          'local': self.platform.endpoint_url_ext}
        self.credentials = dict(region_name=self.platform.region_name,
                                aws_access_key_id=self.platform.aws_access_key_id,
                                aws_secret_access_key=self.platform.aws_secret_access_key,
                                config=self.platform.config)
        self.resource_loc = self.resource(loc_ext='local')
        self.resource_ext = self.resource(loc_ext='external')
        self.client_loc = self.client(loc_ext='local')
        self.client_ext = self.client(loc_ext='external')

    def resource(self, loc_ext='local'):
        return boto3.resource('s3', endpoint_url=self.endpoints[loc_ext], **self.credentials)

    def client(self, loc_ext='local'):
        return boto3.client('s3', endpoint_url=self.endpoints[loc_ext], **self.credentials)

    def s3_file_system(self, obj_name, loc_ext='local'):
        s3 = s3fs.S3FileSystem(anon=False,
                               key=self.platform.aws_access_key_id,
                               secret=self.platform.aws_secret_access_key,
                               client_kwargs={'endpoint_url': self.endpoints[loc_ext]})
        return s3fs.S3Map(root=obj_name, s3=s3, check=False)


class ReadWriteData(ObjectStoreInterface):
    """"Read and write to Zarr on S3"""

    def __init__(self, platform, key_name):
        super().__init__(platform)
        self.s3 = platform
        self.key_name = key_name
        self.obj_name = join(self.bucketname, self.key_name)
        self.file_sys_io = self.get_file_sys_io(self.obj_name)

    def get_file_sys_io(self, obj_name):
        return self.s3_file_system(obj_name)

    def read(self):
        try:
            with xr.open_zarr(self.file_sys_io) as ds:
                return ds
        except (TypeError, GroupNotFoundError):
            ds = None  # Store does not exist
        return ds

    def upload_file(self, local_fname, store_name):
        try:
            try:
                self.client_loc.upload_file(local_fname, self.bucketname, store_name)
            except TypeError:
                self.client_loc.upload_fileobj(local_fname, self.bucketname, store_name)
            print('s3-location: ' + self.bucketname + ' ' + store_name)
        except ClientError as e:
            print(e)

    def to_zarr(self, dataset, append_dim='time'):
        if not any(self.resource_loc.Bucket(self.bucketname).objects.filter(
                Prefix=self.key_name)):
            compressor = zarr.Blosc(cname='zstd', clevel=3, shuffle=2)
            encodings = {v: {'compressor': compressor} for v in
                         list(set(dataset.data_vars.keys())) + list(dataset._coord_names)}
            dataset.to_zarr(store=self.file_sys_io, encoding=encodings, consolidated=True)
        else:
            dataset.to_zarr(store=self.file_sys_io, mode='a', append_dim=append_dim,
                            consolidated=True, compute=False)
        return self.obj_name
