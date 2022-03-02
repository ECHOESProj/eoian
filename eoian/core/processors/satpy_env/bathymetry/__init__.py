#  Copyright (c) 2022.
#  The ECHOES Project (https://echoesproj.eu/) / Compass Informatics

from .spectra_decomp import get_rolling_output


def main(input_file: str, area_wkt: str) -> "Dataset":
    res = get_rolling_output(input_file)
    return res