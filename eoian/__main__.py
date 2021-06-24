#!/usr/bin/env python3

import click
from os.path import join

from eoian.core import SourceDataProducts, processor, Stores


class ProcessingChain:

    def __init__(self, instrument: str, processing_obj: object, area_wkt: str, start, stop, cloud_cover, **kwargs):
        self.instrument = instrument
        self.processing_obj = processing_obj
        self.area_wkt = area_wkt
        self.start = start
        self.stop = stop
        self.cloud_cover = cloud_cover
        self.kwargs = kwargs
        self.store_processed_products()

    def _product_name(self) -> str:
        area = self.area_wkt.replace(' ', '_').replace(',', '!')
        return join(area, self.processing_obj.module)

    def _source_data_products(self):
        return SourceDataProducts(self.area_wkt, self.instrument, self.cloud_cover, self.start, self.stop)

    def _processed_product(self, source_product):
        kwargs = {k: v for k, v in self.kwargs.items() if v is not None}  # Filter out the kwargs with value None
        return self.processing_obj(source_product.product_path, self.area_wkt, **kwargs)

    def processed_products(self):
        for source_product in self._source_data_products():
            try:
                yield source_product.properties, self._processed_product(source_product)
            except Exception as exception:
                print(exception)
                print(f'Error with: {source_product.product_path}')

    def store_processed_products(self) -> None:
        name = self._product_name()
        data_stores = Stores()
        # with Stores() as data_stores:
        for info, dataset in self.processed_products():
            store = data_stores.get_store(name, dataset, info)
            # store.resample()
            store.to_tiff()
            store.metadata_to_json()
            # store.add_attributes_to_dataset().to_zarr()


@click.command()
@click.argument('instrument')
@click.argument('processing_module')
@click.argument('area_wkt')
@click.argument('start')
@click.argument('stop')
@click.option('--cloud_cover', default=None)
@click.option('--graph_path', default=None)
def cli(instrument: str, processing_module: str, area_wkt: str, start: str, stop: str, cloud_cover, graph_path) -> None:
    """

    :param instrument: The name of the instrument (e.g. S1_SAR_GRD)
    :param processing_module: The processor to use.
    :param area_wkt: The WKT string, which is the polygon of the ROI
    :param start: The start date of the search in the format YYYY-MM-DD
    :param stop: The stop date of the search in the format YYYY-MM-DD
    :param cloud_cover: Threshold for allowed cloud cover
    :return:
    """
    click.echo()
    ProcessingChain(instrument, processor(processing_module), area_wkt, start, stop,
                     cloud_cover=cloud_cover, graph_path=graph_path)


if __name__ == '__main__':
    cli()

# S2_MSI_L1C ndvi_s2 "POLYGON ((-6.485367 52.328206, -6.326752 52.328206, -6.326752 52.416241, -6.485367 52.416241, -6.485367 52.328206))" 2021-01-09 2021-02-01 --cloud_cover=90
# S1_SAR_GRD "C:\Users\lavel\OneDrive - Compass Informatics\code\eoian\eoian\resources\graphs\S1_GRD_preprocessing.xml" "C:\Users\lavel\OneDrive - Compass Informatics\code\eoian\eoian\resources\areas\wexfordslobs.geojson" 2021-01-09 2021-02-01
