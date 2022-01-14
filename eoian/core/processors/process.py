#  Copyright (c) 2022.
#  The ECHOES Project (https://echoesproj.eu/) / Compass Informatics

import importlib


class ProcessorBase:

    def __init__(self, module):
        self.module = module
        self.data = None
        self.package = None  # Set this in the child module

    def module_exists(self):
        return importlib.util.find_spec(f'.{self.module}', package=self.package)

    def import_module(self):
        return importlib.import_module(f'.{self.module}', package=self.package)

    def __call__(self, *args, **kwargs):
        processor_module = self.import_module()
        # All processing modules must have a main function
        self.data = processor_module.main(*args, **kwargs)
        return self.data

    def __doc__(self):
        return self.processor.main.__doc__


class ProcessorSatpy(ProcessorBase):

    def __init__(self, module):
        super().__init__(module)
        self.package = 'eoian.core.processors.satpy_env'


class ProcessorSnappy(ProcessorBase):

    def __init__(self, module):
        super().__init__(module)
        self.package = 'eoian.core.processors.snappy_env'


class ProcessorGpt(ProcessorBase):

    def __init__(self, module):
        super().__init__(module)
        self.package = 'eoian.core.processors'


def processor(module: str):
    """

    :param module:
    :return:
    """

    for Processor in ProcessorBase.__subclasses__():
        if (proc := Processor(module)).module_exists():
            return proc
    else:
        raise IOError('Module not found')
