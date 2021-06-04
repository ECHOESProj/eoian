import subprocess
import xarray as xr


def main(input_file: str, area_wkt: str, *, graph_path: str) -> "Dataset":
    output_file = input_file + '.nc'
    cmd = f"""gpt '{graph_path}' -Pinput='{input_file}' -Poutput='{output_file}' -Pgeo_region='{area_wkt}'"""
    print(cmd)
    out = subprocess.call(cmd, shell=True, stdout=subprocess.PIPE)

    if out == 127:
        raise IOError('Error code 127: GPT is not installed')
    elif out != 0:
        raise IOError(f'GPT processing failed, with error code {out}')
    return xr.open_dataset(output_file)
