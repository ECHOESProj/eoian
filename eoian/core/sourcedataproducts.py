import geojson
from eodag.api.core import EODataAccessGateway
from glob import iglob
from os.path import basename
from os.path import join, basename
from shapely.geometry import shape

from .platforms import platform_config


class Area:

    def __init__(self, filename):
        self.geojson = self.get_areas(filename)
        shp = shape(self.geojson)
        self.wkt = shp.wkt

    @staticmethod
    def get_areas(filename):
        with open(filename) as file:
            geo = geojson.load(file)
        return geo


class SourceDataProduct:

    def __init__(self, eodag_product):
        self.eodag_product = eodag_product
        self.properties = eodag_product.properties
        self.properties['objectName'] = 'data.zarr'  # Default zarr name

    def download(self) -> str:
        direc = self.eodag_product.download().replace('file://', '')
        return next(iglob(join(direc, '*.SAFE')))  # TODO: Remove .SAFE to make generic

    def as_dict(self) -> dict:
        return self.product.as_dict()

    def __repr__(self):
        return repr(self.eodag_product)

    def __str__(self):
        return str(self.eodag_product)


class SourceDataProducts:

    def __init__(self, area_wkt, product_type):
        self.platform = platform_config()
        self.area_wkt = area_wkt
        self.product_type = product_type
        self.product_name = None
        self.graph_path = None

    def __call__(self, start, end):
        access_gateway = EODataAccessGateway(self.platform.filename)
        products, estimated_total_nbr_of_results = access_gateway.search(
            productType=self.product_type,
            start=start,
            end=end,
            geom=self.area_wkt)
        for product in products:
            yield SourceDataProduct(product)


def name_from_filename(filename):
    return basename(filename).split('.')[0]


def product_name(area_wkt, processing_module) -> str:
    area = area_wkt.replace(' ', '_').replace(',', '!')
    return join(area, processing_module)
