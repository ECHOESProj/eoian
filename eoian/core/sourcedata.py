#  Copyright (c) 2022.
#  The ECHOES Project (https://echoesproj.eu/) / Compass Informatics

from abc import abstractmethod, abstractproperty
from eodag.api.core import EODataAccessGateway
from glob import iglob
from os.path import basename
from os.path import join, basename
from shapely.geometry import shape

from .settings import configuration


########################################################################################################################
#                                                Base Products                                                         #
########################################################################################################################

class SourceDataProductBase:

    @abstractmethod
    def __init__(self, product: object):
        pass

    @abstractproperty
    def product_path(self) -> str:
        pass


class SourceDataProductsBase:

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

    @abstractmethod
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
        direc = self.eodag_product.download().replace('file://', '')
        return next(iglob(join(direc, '*.SAFE')))  # TODO: Remove .SAFE to make generic


class SourceDataProducts(SourceDataProductsBase):

    def __iter__(self):
        access_gateway = EODataAccessGateway(self.platform.filename)
        products, self.estimated_total_nbr_of_results = access_gateway.search(
            productType=self.product_type,
            start=self.start,
            end=self.end,
            geom=self.area_wkt,
            cloudCover=self.cloud_cover)
        for product in products:
            yield SourceDataProduct(product)
