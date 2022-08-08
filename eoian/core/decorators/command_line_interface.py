import click
import eo_io
from eoian.core.processing_chain import ProcessingChain
from functools import wraps


def to_storage_cli(func):
    @click.command()
    @click.argument('area_wkt')
    @click.argument('date1')
    @click.argument('date2')
    def wrapper_cli(area_wkt: str, date1: str, date2: str) -> None:
        """
        """
        out, metadata = func(area_wkt, date1, date2)
        store = eo_io.store_dataset.store(out, metadata)
        store.to_tiff()
    return wrapper_cli


def processing_chain_cli(to_tiff=True, metadata_to_json=True, to_zarr=True):
    def wrapper_cli_outer(func):
        @wraps(func)
        @click.command()
        @click.argument('instrument')
        @click.argument('area_wkt')
        @click.argument('start')
        @click.argument('stop')
        @click.option('--cloud_cover', default=None)
        @click.option('--graph_path', default=None)
        def wrapper_cli_inner(instrument: str, area_wkt: str, start: str, stop: str,
                              cloud_cover, graph_path) -> None:
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
            processing_chain = ProcessingChain(instrument,
                                               area_wkt,
                                               start,
                                               stop,
                                               processing_func=func,
                                               cloud_cover=cloud_cover,
                                               graph_path=graph_path)
            for d in processing_chain:
                if to_tiff:
                    d.to_tiff()
                if metadata_to_json:
                    d.metadata_to_json()
                if to_zarr:
                    d.to_zarr()
        return wrapper_cli_inner
    return wrapper_cli_outer
