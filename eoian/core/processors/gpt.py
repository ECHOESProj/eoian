import subprocess
import tempfile
from os.path import join, basename, dirname

import xarray as xr

import eoian


def main(input_file: str, area_wkt: str, *, graph_path: str) -> "Dataset":
    # cmd = f"""docker run -v /var/run/docker.sock:/var/run/docker.sock esa-snap /usr/local/snap/bin/gpt '{graph_path}' -Pinput='{input_file}' -Poutput='{output_file}' -Pgeo_region='{area_wkt}'"""
    with tempfile.TemporaryDirectory() as out_netcdf_dir:
        output_netcdf = join(out_netcdf_dir, basename(input_file) + '.nc')
        package_dir = dirname(eoian.__path__[0])
        graphs_dir = join(package_dir, 'eoian/resources/graphs')
        cmd = (f"docker run -v '{graphs_dir}':/tmp/graphs",
               f"-v '{out_netcdf_dir}':'{out_netcdf_dir}'",
               f"-v '{input_file}':'{input_file}'",
               f"-v /var/run/docker.sock:/var/run/docker.sock esa-snap",
               f"/usr/local/snap/bin/gpt '{join('/tmp/graphs/', basename(graph_path))}'",
               f"-Pinput='{input_file}'",
               f"-Poutput='{output_netcdf}'",
               f"-Pgeo_region='{area_wkt}'")
        cmd = ' '.join(cmd)
        # cmd = f"""/usr/local/bin/gpt '{graph_path}' -Pinput='{input_file}' -Poutput='{output_file}' -Pgeo_region='{area_wkt}'"""
        print(cmd)
        out = subprocess.call(cmd, shell=True, stdout=subprocess.PIPE)

        if out == 127:
            raise IOError('Error code 127: GPT is not installed')
        elif out != 0:
            raise IOError(f'GPT processing failed, with error code {out}')
        return xr.open_dataset(output_netcdf)
