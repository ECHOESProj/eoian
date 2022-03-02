#!/usr/bin/env python3

#  Copyright (c) 2022.
#  The ECHOES Project (https://echoesproj.eu/) / Compass Informatics

__author__ = "John Lavelle"
__email__ = "jlavelle@compass.ie"
__version__ = 0.1

import click

from eoian import ProcessingChain, processor


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
    processing_chain = ProcessingChain(instrument, processor(processing_module), area_wkt, start, stop,
                                       cloud_cover=cloud_cover, graph_path=graph_path)
    for d in processing_chain:
        d.to_tiff()
        d.metadata_to_json()
        # d.to_zarr()


if __name__ == '__main__':
    cli()

# S2_MSI_L1C ndvi_s2 "POLYGON ((-6.485367 52.328206, -6.326752 52.328206, -6.326752 52.416241, -6.485367 52.416241, -6.485367 52.328206))" 2021-01-09 2021-02-01 --cloud_cover=90
# S1_SAR_GRD "C:\Users\lavel\OneDrive - Compass Informatics\code\eoian\eoian\resources\graphs\S1_GRD_preprocessing.xml" "C:\Users\lavel\OneDrive - Compass Informatics\code\eoian\eoian\resources\areas\wexfordslobs.geojson" 2021-01-09 2021-02-01
