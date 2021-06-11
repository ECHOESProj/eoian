# eoian: **e**arth **o**bservation processing ch**ain**s







Build the docker image:

    docker build -t eo .
    
Run the container: 
   
    docker run --add-host host.docker.internal:host-gateway eo python3 -m eoian S2_MSI_L1C ndvi_s2 "POLYGON ((-6.485367 52.328206, -6.326752 52.328206, -6.326752 52.416241, -6.485367 52.416241, -6.485367 52.328206))" 2021-01-09 2021-02-01 --cloud_cover=90


## TODO

* Delete downloaded data according to a given policy (e.g. only keep the 10 GB of product files and delete the oldest files).