from os.path import join
from .sourcedata import SourceDataProducts
import eo_io
from typing import Callable, Any


class ProcessingChain:

    def __init__(self, instrument: str, processing_func: Callable[..., Any], area_wkt: str, start: str, stop: str,
                 cloud_cover: int, **kwargs: dict):
        self.instrument = instrument
        self.processing_func = processing_func
        self.area_wkt = area_wkt
        self.start = start
        self.stop = stop
        self.cloud_cover = cloud_cover
        self.kwargs = kwargs

    def product_name(self) -> str:
        area = self.area_wkt.replace(' ', '_').replace(',', '!')
        return join(area, self.processing_func.__name__)

    def source_data(self):
        return SourceDataProducts(self.area_wkt, self.instrument, self.cloud_cover, self.start, self.stop)

    def process(self, source_product):
        kwargs = {k: v for k, v in self.kwargs.items() if v is not None}  # Filter out the kwargs with value None
        return self.processing_func(source_product.product_path, self.area_wkt, **kwargs)

    def __iter__(self):
        name = self.product_name()
        for source_product in self.source_data():
            dataset = self.process(source_product)
            md = source_product.properties
            metadata = eo_io.store_dataset.Metadata(name, md['platform'], md['instrument'], md['processingLevel'],
                                                    md['startTimeFromAscendingNode'], md['id'],
                                                    md['relativeOrbitNumber'], md['platformSerialIdentifier'])
            store = eo_io.store_dataset.store(dataset, metadata)
            yield store
