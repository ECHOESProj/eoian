FROM ubuntu:20.04

ARG ssh_prv_key
ARG ssh_pub_key

ENV TZ=Europe/Dublin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone && \
    apt-get update && \
    apt-get install -y python3-pip binutils netcdf-bin libproj-dev gdal-bin libnetcdf-dev \
    libhdf5-serial-dev libproj-dev libgeos-dev proj-data proj-bin docker.io git

COPY ./requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt

# Authorize SSH Host
RUN mkdir -p /root/.ssh && \
    chmod 0700 /root/.ssh && \
    ssh-keyscan github.com > /root/.ssh/known_hosts && \
    echo "$ssh_prv_key" > /root/.ssh/id_rsa && \
    chmod 600 /root/.ssh/id_rsa


RUN pip3 install git+ssh://git@github.com/ECHOESProj/eo-io@main#egg=eo-io && \
    pip3 install git+ssh://git@github.com/ECHOESProj/eoian@main#egg=eoian && \
    pip3 install git+https://github.com/dcs4cop/xcube.git

COPY ./eoian /app/eoian
WORKDIR /app/

ENTRYPOINT  [ "python3", "-W", "ignore", "-m", "eoian" ]
