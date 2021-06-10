#!/usr/bin/env python3

import click
from eoian.core import SourceDataProducts, processor, product_name, Stores


def processed_products(instrument, processing_module, area_path, start, stop, **kwargs):
    prods = SourceDataProducts(area_path, instrument)
    for product in prods(start, stop):
        print(f"{product=}")
        product_filename = product.download()
        info = product.properties
        try:
            yield info, processing_module(product_filename, prods.area_wkt, **kwargs)
        except Exception as exception:
            print(exception)
            raise


def process_batches(instrument: str, processing_module: object, area_wkt: str, start, end, **kwargs) -> None:
    datacube_name = product_name(area_wkt, processing_module.module, **kwargs)
    data_stores = Stores()
    for info, dataset in processed_products(instrument, processing_module, area_wkt, start, end, **kwargs):
        store = data_stores.get_store(datacube_name, dataset, info)
        store.to_tiff()
        store.metadata_to_json()
        # store.resample().add_metadata_to_dataset().to_zarr()


@click.command()
@click.argument('instrument')
@click.argument('processing_module')
@click.argument('area_wkt')
@click.argument('start')
@click.argument('end')
def cli(instrument: str, processing_module: str, area_wkt: str, start: str, end: str) -> None:
    """

    :param instrument: The name of the instrument (e.g. S1_SAR_GRD)
    :param processing_module: The processor to use. Either a path to xml file for the GPT
                              processor or the name of the Python module
    :param area_wkt: The path to the region of interest file
    :param start: The start date of the search in the format YYYY-MM-DD
    :param end: The end date of the search in the format YYYY-MM-DD
    :return:
    """
    click.echo()
    if processing_module.endswith('.xml'):
        processing_module = 'gpt'
        kwargs = {'graph_path': processor}
    else:
        kwargs = {}
    process_batches(instrument, processor(processing_module), area_wkt, start, end, **kwargs)


if __name__ == '__main__':
    cli()

# S1_SAR_GRD "C:\Users\lavel\OneDrive - Compass Informatics\code\eoian\eoian\resources\graphs\S1_GRD_preprocessing.xml" "C:\Users\lavel\OneDrive - Compass Informatics\code\eoian\eoian\resources\areas\wexfordslobs.geojson" 2021-01-09 2021-02-01
