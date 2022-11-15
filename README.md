# eoian: **e**arth **o**bservation processing ch**ain**s

The individual processors are in

    eoian/eoian/core/processors

These can be called directly from the eoain processing chain, as described below.

New processor will be added to the [eo-processors](https://github.com/ECHOESProj/eo-processors) repository, 
which imports the eoain package.  

The code in eoian/eoian/core/processors/snappy_env is legacy code,
that had not been integrated into the processing chain.


## Docker 


Build the docker image:

    docker build -t eoian .
 
## Usage

The processors are being moved to a [separate repository](https://github.com/ECHOESProj/eo-processors).
The code in this repository imports the eoian package. 
The legacy processors can be called via the CLI, as described below. 

The NDVI processor can be called as follows:

    python3 S2_MSI_L1C ndvi_s2 "POLYGON ((-6.485367 52.328206, -6.326752 52.328206, -6.326752 52.416241, -6.485367 52.416241, -6.485367 52.328206))" 2021-01-09 2021-02-01 --cloud_cover=90

The Sentinel-1 backscatter processor can be called as follwos:

    S1A_IW_GRDH_1SDV backscatter_s1 "POLYGON ((-6.485367 52.328206, -6.326752 52.328206, -6.326752 52.416241, -6.485367 52.416241, -6.485367 52.328206))" 2021-01-09 2021-02-01

 The processors can be run using Docker, as in the following example: 

    docker run -v /var/run/docker.sock:/var/run/docker.sock -v /data:/data --network host eoian S2_MSI_L1C ndvi_s2 "POLYGON ((-6.485367 52.328206, -6.326752 52.328206, -6.326752 52.416241, -6.485367 52.416241, -6.485367 52.328206))" 2021-01-09 2021-02-01 --cloud_cover=90   


The output location is written to stdout, with the prefix, for example:

    s3-location: compass-eo POLYGON_((-6.485367_52.328206!_-6.326752_52.328206!_-6.326752_52.416241!_-6.485367_52.416241!_-6.485367_52.328206))/ndvi_s2/Sentinel-2/MSI/L1C/2021/01/25/S2B_MSIL1C_20210125T114349_N0209_R123_T29UPU_20210125T122833.tif
    s3-location: compass-eo POLYGON_((-6.485367_52.328206!_-6.326752_52.328206!_-6.326752_52.416241!_-6.485367_52.416241!_-6.485367_52.328206))/ndvi_s2/Sentinel-2/MSI/L1C/2021/01/25/S2B_MSIL1C_20210125T114349_N0209_R123_T29UPU_20210125T122833.json
        

