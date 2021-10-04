=======================
Command Line User Guide
=======================


Existing processors can be run through the CLI.

Eoian should be run using the "-m" flag.

.. code-block:: console

    $ python3 -m eoian --help
    Usage: python -m eoian [OPTIONS] INSTRUMENT PROCESSING_MODULE AREA_WKT START
                           STOP

      :param instrument: The name of the instrument (e.g. S1_SAR_GRD)
      :param processing_module: The processor to use.
      :param area_wkt: The WKT string, which is the polygon of the ROI
      :param start: The start date of the search in the format YYYY-MM-DD
      :param stop: The stop date of the search in the format YYYY-MM-DD
      :param cloud_cover: Threshold for allowed cloud cover
      :return:

    Options:
      --cloud_cover TEXT
      --graph_path TEXT
      --help              Show this message and exit.


This is an example for processing of NDVI:

.. code-block:: console

    eoain S2_MSI_L1C ndvi_s2 "POLYGON ((-6.485367 52.328206, -6.326752 52.328206, -6.326752 52.416241, -6.485367 52.416241, -6.485367 52.328206))" 2021-01-09 2021-02-01 --cloud_cover=90

This processing chain uses Sentinel-2 L1C (S2_MSI_L1C) for the source instrument.

The area "area_wkt" argument specifies the bounding box of the processing, given in WKT format.

The processing is done between the date interval ["start", "stop"].

Tiles with a percentage cloud cover greater than cloud_cover will be filtered out.

The output will be stored in GeoTIFFs in the object store.


Using Docker
------------

The first step is to build the docker image:

.. code-block:: console

    $ docker build -t eo .


Then run the container with:

.. code-block:: console

    $ docker run -v /var/run/docker.sock:/var/run/docker.sock -v /data:/data --network host eom S2_MSI_L1C ndvi_s2 "POLYGON ((-6.485367 52.328206, -6.326752 52.328206, -6.326752 52.416241, -6.485367 52.416241, -6.485367 52.328206))" 2021-01-09 2021-02-01 --cloud_cover=90


The output location is written to stdout, with the prefix, for example:

.. code-block:: console

    >> s3-location: compass-eo POLYGON_((-6.485367_52.328206!_-6.326752_52.328206!_-6.326752_52.416241!_-6.485367_52.416241!_-6.485367_52.328206))/ndvi_s2/Sentinel-2/MSI/L1C/2021/01/25/S2B_MSIL1C_20210125T114349_N0209_R123_T29UPU_20210125T122833.tif
    >> s3-location: compass-eo POLYGON_((-6.485367_52.328206!_-6.326752_52.328206!_-6.326752_52.416241!_-6.485367_52.416241!_-6.485367_52.328206))/ndvi_s2/Sentinel-2/MSI/L1C/2021/01/25/S2B_MSIL1C_20210125T114349_N0209_R123_T29UPU_20210125T122833.json


S2_MSI_L1C ndvi_s2 "POLYGON ((-6.485367 52.328206, -6.326752 52.328206, -6.326752 52.416241, -6.485367 52.416241, -6.485367 52.328206))" 2021-01-09 2021-02-01 --cloud_cover=90

S1A_IW_GRDH_1SDV backscatter_s1 "POLYGON ((-6.485367 52.328206, -6.326752 52.328206, -6.326752 52.416241, -6.485367 52.416241, -6.485367 52.328206))" 2021-01-09 2021-02-01

CREODIAS has over 20 PB of EO data available. Eoian automates the access to and process the data.
