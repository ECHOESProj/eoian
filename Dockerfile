FROM ubuntu:20.04

ENV TZ=Europe/Dublin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone && \
    apt-get update && \
    apt-get install -y python3-pip binutils netcdf-bin libproj-dev gdal-bin libnetcdf-dev \
    libhdf5-serial-dev libproj-dev libgeos-dev proj-data proj-bin docker.io git

RUN pip3 install git+ssh://git@github.com/ECHOESProj/eo-io.git
COPY ./requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt

COPY ./eo-io /tmp/eo-io
RUN ls /tmp/eo-io/
RUN pip3 install /tmp/eo-io/

COPY ./eoian /app/eoian
WORKDIR /app/

ENTRYPOINT  [ "python3", "-W", "ignore", "-m", "eoian" ]
