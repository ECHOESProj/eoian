#  Copyright (c) 2022.
#  The ECHOES Project (https://echoesproj.eu/) / Compass Informatics

import numpy as np
from pyproj import Proj, itransform
from pyresample.geometry import create_area_def


def reproject(in_proj, out_proj, xs, ys):
    proj_in = Proj(init="epsg:" + str(in_proj))
    proj_out = Proj(init="epsg:" + str(out_proj))
    new_x, new_y = list(zip(*itransform(proj_in, proj_out, zip(*[xs, ys]), always_xy=True)))
    return np.array(new_x), np.array(new_y)

def get_bounds(area, out_proj_espg_num):
    xmin, ymin, xmax, ymax = area.bounds
    (nxmin, nxmax), (nymin, nymax) = reproject(4326, out_proj_espg_num, (xmin, xmax), (ymin, ymax))
    return nxmin, nymin, nxmax, nymax


def area_def(area_extent, resolution):
    proj_dict = {'proj': 'longlat', 'datum': 'WGS84'}
    return create_area_def('ROI', proj_dict, units='degrees', area_extent=area_extent, resolution=resolution)