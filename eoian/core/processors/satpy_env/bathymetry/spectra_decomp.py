import pickle
from os.path import dirname

import dask
import geopandas as gpd
import numpy as np
import xarray as xr
from satpy import Scene, find_files_and_readers
from satpy.dataset import DataQuery
from scipy import fftpack

sub_size = 256
Ncomps = 64

df_europe = gpd.read_file("eoian/data/europe_coastline/Europe_coastline_poly.shp")


# df_europe.intersection(b).area.sum() / shape(b).area


def get_data(input_file):
    files = find_files_and_readers(base_dir=dirname(input_file), reader='sar-c_safe')
    scn = Scene(filenames=files)
    hh_id = DataQuery(name="measurement", polarization="vv")
    lat_id = DataQuery(name='latitude', polarization='vv')
    lon_id = DataQuery(name='longitude', polarization='vv')
    scn.load([hh_id, lat_id, lon_id])
    ds = scn.to_xarray_dataset()
    ds['latitude'] = scn['latitude']
    ds['longitude'] = scn['longitude']
    return ds


def get_rolling(dataset, sub_size, stride=sub_size // 2):
    with dask.config.set(**{'array.slicing.split_large_chunks': True}):
        return dataset.rolling({'x': sub_size, 'y': sub_size}, center=True). \
            construct(x='wx', y='wy', stride=stride).chunk()


def spectra_amplitude(arr):
    """
    Compute spectral amplitude using 2D FFT
    """
    arr = arr - arr.mean()
    arr_fft = fftpack.fftn(arr)  # fft
    spectral_amp_arr = fftpack.fftshift(np.abs(arr_fft))
    return spectral_amp_arr


def get_specs(ds_roll, sub_size):
    return xr.apply_ufunc(spectra_amplitude,
                          ds_roll['measurement'],
                          input_core_dims=[['wx', 'wy']],
                          output_core_dims=[['xx', 'yy']],
                          output_dtypes=[float],
                          dask_gufunc_kwargs={'output_sizes': {'xx': sub_size, 'yy': sub_size}},
                          dask='parallelized',
                          vectorize=True)


class ComponentWeights:

    def __init__(self):
        self.transformer = pickle.load(open('data/pca_256.pkl', 'rb'))

    def get_pca_weights(self, spectral_amp_arr):
        """
        Parameters:
            spectral_amp_arr
        Return:
            the PCA weights
        """
        if np.isnan(spectral_amp_arr).any():
            weights = np.arange(Ncomps).astype(float)
            weights.fill(np.nan)
        else:
            weights = self.transformer.transform([spectral_amp_arr.ravel()])[0][0: Ncomps]
        return weights


def get_rolling_output(input_file):
    ds = get_data(input_file)
    ds_roll = get_rolling(ds, sub_size)

    specs = get_specs(ds_roll, sub_size)

    lon_lat = ds_roll[['longitude', 'latitude']].mean(dim=['wx', 'wy'])
    lon_lat_z = lon_lat.stack(z=('x', 'y'))
    df_europe.mask(lon_lat_z['longitude'], lon_lat_z['latitude'])

    cw = ComponentWeights()
    components = xr.apply_ufunc(cw.get_pca_weights,
                                specs,
                                input_core_dims=[['x', 'y']],
                                output_core_dims=[['component']],
                                output_dtypes=[float],
                                dask_gufunc_kwargs={'output_sizes': {'component': Ncomps}},
                                dask='parallelized',
                                vectorize=True)
    return specs
