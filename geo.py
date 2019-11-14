# -*- coding: utf-8 -*-

from pyproj import Proj, transform


def epsg_trafo(x_in, y_in, from_coords="epsg:3857", to_coords="epsg:4326", invert=False):
    """
    transform coodinates from coordinate system 'from_coords' to coodinate system
    'to_coords' find the right coordinate system names at https://epsg.io
    """
    in_proj = Proj(init=from_coords)
    out_proj = Proj(init=to_coords)
    x_out, y_out = transform(in_proj, out_proj, x_in, y_in)
    return (y_out, x_out) if invert else (x_out, y_out)
