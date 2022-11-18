"""
Get processing module
"""

import importlib
from typing import Union, Any, Callable


def _module_exists_in_package(module_name, _package) -> bool:
    spec = importlib.util.find_spec(f'.{module_name}', package=_package)
    return True if spec else False


def _get_module(module, package):
    if package:
        packages = [package, ]
    else:  # list of packages to check if the module exists
        packages = ['eoian.core.processors.satpy_env',
                    'eoian.core.processors.snappy_env',
                    'eoian.core.processors.snappy_env']

    for _package in packages:
        if _module_exists_in_package(module, _package):
            _module = importlib.import_module(f'.{module}', package=_package)
            break
    else:
        raise IOError('Module not found')
    return _module


def processor(module: str, package: str = None) -> Callable:
    """
    @param module: str  # the name of the module
    @param package: str  # the name of the package
    @return: Callable  # the main function in the module
    """

    _module = _get_module(module, package)

    def func(input_file: str, area_wkt: str, **kwargs: Any) \
            -> Union["xr.Dataset", "xr.DataArray", "sp.dataset"]:
        return _module.main(input_file, area_wkt, **kwargs)  # All processing modules must have a main function

    return func
