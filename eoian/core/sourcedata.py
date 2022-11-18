import abc
from glob import iglob
from os.path import join

from eodag.api.core import EODataAccessGateway

from eo_io import configuration


########################################################################################################################
#                                                Base Products                                                         #
########################################################################################################################

class SourceDataProductBase(abc.ABC):

    @abc.abstractmethod
    def __init__(self, product: object):
        self.product = product

    @abc.abstractmethod
    def product_path(self) -> str:
        pass


class SourceDataProductsBase(abc.ABC):

    def __init__(self, area_wkt, product_type, cloud_cover, start, end):
        self.platform = configuration()
        self.area_wkt = area_wkt
        self.cloud_cover = cloud_cover
        self.product_type = product_type
        self.product_name = None
        self.graph_path = None
        self.start = start
        self.end = end
        self.estimated_total_nbr_of_results = None
        self.access_gateway = self.get_access_gateway()

    @abc.abstractmethod
    def get_access_gateway(self):
        pass

    @abc.abstractmethod
    def __iter__(self):
        pass


########################################################################################################################
#                                                     Using EODag                                                      #
########################################################################################################################


class SourceDataProduct(SourceDataProductBase):

    def __init__(self, eodag_product):
        self.eodag_product = eodag_product
        self.properties = eodag_product.properties
        self.properties['objectName'] = 'data.zarr'  # Default zarr name

    @property
    def product_path(self) -> str:
        full_path = self.eodag_product.download().replace('file://', '')
        direc = '/'.join(full_path.split('/')[:-1])
        return next(iglob(join(direc, '*.*')))


class SourceDataProducts(SourceDataProductsBase):

    def get_access_gateway(self):
        return EODataAccessGateway(self.platform.filename)

    def __iter__(self):
        product_types = [t['ID'] for t in self.access_gateway.list_product_types()]
        if self.product_type not in product_types:
            raise ValueError(f"Product type {self.product_type} is not valid."
                             f"\n\tValid product types:\n\t{product_types}")
        products, self.estimated_total_nbr_of_results = self.access_gateway.search(
            productType=self.product_type,
            start=self.start,
            end=self.end,
            geom=self.area_wkt,
            cloudCover=self.cloud_cover)
        for product in products:
            yield SourceDataProduct(product)
