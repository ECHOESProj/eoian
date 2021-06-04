from dataclasses import dataclass
from abc import abstractmethod, ABC
import urllib
from socket import timeout
from botocore.client import Config
import yaml
from glob import glob
from os.path import join
from pathlib import Path
import os


@dataclass
class Configuration:
    platform: str
    priority: int
    filename: str
    region_name: str
    endpoint_url_local: str
    endpoint_url_ext: str
    aws_access_key_id: str
    aws_secret_access_key: str
    config: object
    output_directory: str
    bucket: str

    def is_storage_accessible(self) -> bool:
        """
        Call from am_i_on_this_platform() to check that url is accessible on this platform
        If we get some response from the endpoint_url_local then we know we are on that
        platform.
        """
        print(f'{self.endpoint_url_local=}')
        try:
            status = urllib.request.urlopen(self.endpoint_url_local, timeout=2).status == 200
        except urllib.error.HTTPError:
            print('urllib.error.HTTPError')
            status = True
        except urllib.error.URLError:
            print('urllib.error.URLError')
            status = False
        except timeout:
            print('timeout')
            status = False
        return status

    def am_i_on_this_platform(self) -> bool:
        try:
            # The fast check
            on_platform = (self.platform == os.environ['DATA_SINK'])
        except KeyError:
            # The slow check
            on_platform = self.is_storage_accessible()
            if on_platform:
                # Set the environment variable so that next time it will be fast
                os.environ['DATA_SINK'] = self.platform
        return on_platform


def read_yaml(file_name):
    with open(file_name) as f:
        return yaml.load(f.read(), Loader=yaml.FullLoader)


def configs():
    for file_name in glob(join(Path(__file__).parent.parent, 'config', '*.yaml')):
        config_yaml = read_yaml(file_name)
        platform_name = list(config_yaml.keys())[0]
        platform = config_yaml[platform_name]['storage']
        platform['priority'] = config_yaml[platform_name]['priority']
        platform['platform'] = platform_name
        platform['filename'] = file_name
        platform['config'] = eval(platform['config']) if platform['config'] else None
        platform = Configuration(**platform)
        yield platform


def platform_config():
    config_dict = {platform.platform: platform for platform in configs()}
    # sort so the highest priority comes first
    configs_list = sorted(configs(), key=lambda c: c.priority, reverse=True)
    try:
        # The case where the data source is given by the environment variable
        data_source_platform = config_dict[os.environ['DATA_SOURCE']]
    except KeyError:
        # Otherwise get the highest priority data source
        data_source_platform = configs_list[0]
        os.environ['DATA_SOURCE'] = data_source_platform.platform 

    # If we are not on the data_source_platform we cannot store there, so find where we can
    for platform in configs_list:
        if platform.am_i_on_this_platform():
            print(f'{platform=}')
            break
    else:
        raise IOError('Could not determine the platform')

    if data_source_platform != platform:
        # Copy the platform config (which contains the store info) to data_source_platform config
        for v in ['endpoint_url_local', 'endpoint_url_ext', 'aws_access_key_id', 'aws_secret_access_key',
                  'config', 'output_directory']:
            setattr(data_source_platform, v, getattr(platform, v))

    print(data_source_platform)
    return data_source_platform


if __name__ == '__main__':
    print(platform_config())
