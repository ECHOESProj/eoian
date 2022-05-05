import numpy as np
import xarray as xr
from satpy.readers.olci_nc import BitFlags


@xr.register_dataarray_accessor("apply_mask")
class Mask(object):
    """Add a method to xr.DataArray for masking a satpy-dataset."""

    def __init__(self, xarray_obj):
        self._obj = xarray_obj
        self._mask = None

    def get_boolean_mask(self, flags=None):
        """Returns a boolean mask for the specified flags."""
        bflags = BitFlags(self._mask)
        self._obj.attrs['flags'] = bflags.flag_list
        if flags is None:
            flags = bflags.flag_list  # Use all the flags
        return xr.concat([bflags[item] for item in flags], 'flag')

    @property
    def bitmask(self):
        return self._mask

    @bitmask.setter
    def bitmask(self, values):
        """Set with the decoded bitmask"""
        if not np.issubdtype(values, np.integer):
            raise ValueError('The bitmask should integers')
        self._mask = values

    def __call__(self, flags=None):
        """Returns a filtered dataset. It is filtered (i.e. set to a
        nan values) where any of the the specified flag's values are true, for a
        given pixel.

        Example usage:
            # Create the scene object and load the dataset.
            scn = Scene(filenames=files) # The S3-l1 files must be included.
            scn.load(['dataset_name', 'wqsf']) # The bitmask must be loaded
            da = scn['dataset_name']

            da.flags # Returns a list of all the available flags names.

            # List of flags to filter with. Here, we want to filter cloud pixels.
            flags = ['CLOUD', 'CLOUD_AMBIGUOUS', 'CLOUD_MARGIN']

            # Return a xr.DataArray with the masked values set to nans,
            # for the specified list of flags names.
            da.apply_mask(flags)
            # With flags=None, *all* the flags would be used to filter.

            # Return a boolean mask (xr.DataArray) for the corresponding flags.
            da.apply_mask.get_boolean_mask(flags)
            # The dimensions of the boolean mask area are (flag, y, x), where
            # flag is the length of flags.
            # With flags=None, the boolean mask for *all* flags is returned

        Args:
            flags: iterator containing the flag names. With flags=None, all
                   flags are used to filter.
        Returns:
            class: `xarray.DataArray`
        """
        if self._mask is None:
            raise ValueError("""The 'wqsf' dataset needs to be loaded for this 
            method to work. The 'wqsf' data is in the Level-1 S3 files.""")
        bool_mask_2d = self.get_boolean_mask(flags).reduce(func=np.any,
                                                           dim='flag')
        return self._obj.where(~bool_mask_2d)
