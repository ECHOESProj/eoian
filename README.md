# eoian: **e**arth **o**bservation processing ch**ain**s


Build the docker image:

    docker build -t eo .
    
Run the container: 

    docker run -v /var/run/docker.sock:/var/run/docker.sock -v /data:/data --network host eo S2_MSI_L1C ndvi_s2 "POLYGON ((-6.485367 52.328206, -6.326752 52.328206, -6.326752 52.416241, -6.485367 52.416241, -6.485367 52.328206))" 2021-01-09 2021-02-01 --cloud_cover=90   


The output location is written to stdout, with the prefix, for example:

    s3-location: compass-eo POLYGON_((-6.485367_52.328206!_-6.326752_52.328206!_-6.326752_52.416241!_-6.485367_52.416241!_-6.485367_52.328206))/ndvi_s2/Sentinel-2/MSI/L1C/2021/01/25/S2B_MSIL1C_20210125T114349_N0209_R123_T29UPU_20210125T122833.tif
    s3-location: compass-eo POLYGON_((-6.485367_52.328206!_-6.326752_52.328206!_-6.326752_52.416241!_-6.485367_52.416241!_-6.485367_52.328206))/ndvi_s2/Sentinel-2/MSI/L1C/2021/01/25/S2B_MSIL1C_20210125T114349_N0209_R123_T29UPU_20210125T122833.json


S2_MSI_L1C ndvi_s2 "POLYGON ((-6.485367 52.328206, -6.326752 52.328206, -6.326752 52.416241, -6.485367 52.416241, -6.485367 52.328206))" 2021-01-09 2021-02-01 --cloud_cover=90

S1A_IW_GRDH_1SDV backscatter_s1 "POLYGON ((-6.485367 52.328206, -6.326752 52.328206, -6.326752 52.416241, -6.485367 52.416241, -6.485367 52.328206))" 2021-01-09 2021-02-01

=======

Deploy:

    #local:
    git archive main --output deploy.zip 
    pscp deploy.zip eouser@eo-stack:/home/eouser/

    #remote:
    unzip deploy.zip -d eoian
    docker build eoian -t eo --network host
>>>>>>> e22c6e3a5a5ad8a62074c2e0fc4bf3b6846d1a65
