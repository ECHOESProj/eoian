from os.path import join
from .sourcedata import SourceDataProducts
import eo_io


class ProcessingChain:

    def __init__(self, instrument: str, processing_obj: object, area_wkt: str, start: str, stop: str,
                 cloud_cover: int,
                 **kwargs: dict):
        self.instrument = instrument
        self.processing_obj = processing_obj
        self.area_wkt = area_wkt
        self.start = start
        self.stop = stop
        self.cloud_cover = cloud_cover
        self.kwargs = kwargs

    def product_name(self) -> str:
        area = self.area_wkt.replace(' ', '_').replace(',', '!')
        return join(area, self.processing_obj.module)

    def source_data(self):
        return SourceDataProducts(self.area_wkt, self.instrument, self.cloud_cover, self.start, self.stop)

    def process(self, source_product):
        kwargs = {k: v for k, v in self.kwargs.items() if v is not None}  # Filter out the kwargs with value None
        return self.processing_obj(source_product.product_path, self.area_wkt, **kwargs)

    def __iter__(self):
        name = self.product_name()
        for source_product in self.source_data():
            dataset = self.process(source_product)
            store = eo_io.store_dataset.store(dataset, name, source_product.properties)
            yield store
