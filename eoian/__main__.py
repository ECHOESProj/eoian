#!/usr/bin/env python3

import click
from eoian.core import SourceDataProducts, processor, product_name, Stores


def processed_products(instrument, processing_module, area_wkt, start, stop, cloud_cover, **kwargs):
    for source_product in SourceDataProducts(area_wkt, instrument, cloud_cover, start, stop):
        try:
            processed_product = processing_module(source_product.product_path, area_wkt, **kwargs)
            yield source_product.properties, processed_product
        except Exception as exception:
            print(exception)


def store_processed_products(instrument: str, processing_module: object, area_wkt: str, start, end, cloud_cover,
                             **kwargs) -> None:
    name = product_name(area_wkt, processing_module.module, **kwargs)
    with Stores() as data_stores:
        for info, dataset in processed_products(instrument, processing_module, area_wkt, start, end, cloud_cover,
                                                **kwargs):
            store = data_stores.get_store(name, dataset, info)
            store.to_tiff()
            store.metadata_to_json()
            # store.resample().add_attributes_to_dataset().to_zarr()


@click.command()
@click.argument('instrument')
@click.argument('processing_module')
@click.argument('area_wkt')
@click.argument('start')
@click.argument('end')
@click.option('--cloud_cover', default=None)
def cli(instrument: str, processing_module: str, area_wkt: str, start: str, end: str, cloud_cover) -> None:
    """

    :param instrument: The name of the instrument (e.g. S1_SAR_GRD)
    :param processing_module: The processor to use. Either a path to xml file for the GPT
                              processor or the name of the Python module
    :param area_wkt: The WKT string, which is the polygon of the ROI
    :param start: The start date of the search in the format YYYY-MM-DD
    :param end: The end date of the search in the format YYYY-MM-DD
    :param cloud_cover: Threshold for allowed cloud cover
    :return:
    """
    click.echo()
    if processing_module.endswith('.xml'):
        processing_module = 'gpt'
        kwargs = {'graph_path': processor}
    else:
        kwargs = {}
    store_processed_products(instrument, processor(processing_module), area_wkt, start, end, cloud_cover, **kwargs)


if __name__ == '__main__':
    cli()

# S1_SAR_GRD "C:\Users\lavel\OneDrive - Compass Informatics\code\eoian\eoian\resources\graphs\S1_GRD_preprocessing.xml" "C:\Users\lavel\OneDrive - Compass Informatics\code\eoian\eoian\resources\areas\wexfordslobs.geojson" 2021-01-09 2021-02-01
