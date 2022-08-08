from os.path import join
from .sourcedata import SourceDataProducts
import eo_io
from typing import Callable, Any


class ProcessingChain:

    def __init__(self, instrument: str, area_wkt: str, start: str, stop: str,
                 cloud_cover: int, processing_func: Callable[..., Any] = None, **kwargs: dict):
        self.instrument = instrument
        self.processing_func = processing_func
        self.area_wkt = area_wkt
        self.start = start
        self.stop = stop
        self.cloud_cover = cloud_cover
        self.kwargs = kwargs
        self.access_gateway = None

    def product_name(self) -> str:
        if self.processing_func:
            area = self.area_wkt.replace(' ', '_').replace(',', '!')
            return join(area, self.processing_func.__name__)
        else:
            return ''

    def source_data(self):
        source_data = SourceDataProducts(self.area_wkt, self.instrument, self.cloud_cover, self.start, self.stop)
        self.access_gateway = source_data.access_gateway
        return source_data

    def process(self, source_product):
        kwargs = {k: v for k, v in self.kwargs.items() if v is not None}  # Filter out the kwargs with value None
        if self.processing_func:
            return self.processing_func(source_product.product_path, self.area_wkt, **kwargs)
        else:
            return None

    def __iter__(self):
        product_directory = self.product_name()
        for source_product in self.source_data():
            dataset = self.process(source_product)
            md = source_product.properties
            metadata = eo_io.metadata.Metadata(source_product, product_directory, md['platform'], md['instrument'],
                                                    md['processingLevel'], md['startTimeFromAscendingNode'], md['id'],
                                                    md['relativeOrbitNumber'], md['platformSerialIdentifier'])
            store = eo_io.store_dataset.store(dataset, metadata)
            yield store
