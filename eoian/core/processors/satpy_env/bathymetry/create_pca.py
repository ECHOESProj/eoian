#  Copyright (c) 2022.
#  The ECHOES Project (https://echoesproj.eu/) / Compass Informatics

import pickle

import xarray as xr
from sklearn.decomposition import IncrementalPCA
from .spectra_decomp import *


class Components:

    def __init__(self, sub_size=256, n_components=64):
        self.sub_size = sub_size
        self.n_components = n_components
        self.transformer = self.get_transformer()

    def get_transformer(self):
        try:
            transformer = pickle.load(open('data/pca_256.pkl', 'rb'))
        except FileNotFoundError:
            transformer = IncrementalPCA(n_components=7, batch_size=200)
        return transformer

    def transform(self, specs):
        X = specs.fillna(0).stack(z=('x', 'y'))
        self.transformer.partial_fit(X)
        pickle.dump(self.transformer, open('data/pca_256.pkl', 'wb'))


def main(input_file: str, area_wkt: str) -> "Dataset":

    ds = get_data(input_file)
    ds_roll = get_rolling(ds, sub_size)
    specs = get_specs(ds_roll, sub_size)
    c = Components()
    c.transform(specs)

    # comps = Components()
    # print(input_file)
    # comps.transform(input_file)
    return specs
