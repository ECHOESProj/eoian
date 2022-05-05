#  Copyright (c) 2022.
#  The ECHOES Project (https://echoesproj.eu/) / Compass Informatics

"""
Get processing module
"""

import importlib
from typing import Union, Any, Callable
from types import ModuleType


class Processor:

    def __init__(self, module_name: str):
        self.module_name = module_name
        self._package = None
        self.processor_module = None

    def _module_exists_in_package(self) -> bool:
        spec = importlib.util.find_spec(f'.{self.module_name}', package=self._package)
        return True if spec else False

    def _import_module(self) -> ModuleType:
        return importlib.import_module(f'.{self.module_name}', package=self._package)

    @property
    def package(self):
        return self._package

    @package.setter
    def package(self, package):
        self._package = package
        if not self._module_exists_in_package():
            raise ModuleNotFoundError('Module not found in this package')

    def __call__(self, input_file: str, area_wkt: str, **kwargs: Any) \
            -> Union["xr.Dataset", "xr.DataArray", "sp.dataset"]:
        self.processor_module = self._import_module()
        return self.processor_module.main(input_file, area_wkt,
                                          **kwargs)  # All processing modules must have a main function

    def __doc__(self) -> str:
        return self.processor_module.main.__doc__

    @property
    def __name__(self) -> str:
        return self.module_name


# class ProcessorDocker(Processor):
#
#     def run_in_docker(self, function_file):
#         #  docker function_file
#
#     def __call__(self, input_file: str, area_wkt: str, **kwargs: Any) \
#             -> Union["xr.Dataset", "xr.DataArray", "sp.dataset"]:
#         self.processor_module = self._import_module()
#         return self.processor_module.main(input_file, area_wkt,
#                                           **kwargs)  # All processing modules must have a main function

def get_packages(package):
    if package:
        packages = [package, ]
    else:  # list of packages to check if the module exists
        packages = ['eoian.core.processors.satpy_env',
                    'eoian.core.processors.snappy_env',
                    'eoian.core.processors.snappy_env']
    for _package in packages:
        yield _package


def processor(module: str, package: str = None) -> Callable:
    """
    @param module: str  # the name of the module
    @param package: str  # the name of the package
    @return: Callable  # the main function in the module
    """
    processor_callable = Processor(module)
    for _package in get_packages(package):
        try:
            processor_callable.package = _package
            return processor_callable
        except ModuleNotFoundError:
            pass
    else:
        raise ModuleNotFoundError
