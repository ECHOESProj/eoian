FROM ubuntu:20.04

ENV TZ=Europe/Dublin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone && \
    apt-get update && \
    apt-get install -y python3-pip python3-gdal binutils netcdf-bin libproj-dev gdal-bin libnetcdf-dev \
    libhdf5-serial-dev libproj-dev libgeos-dev proj-data proj-bin docker.io git

COPY ./requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt

# Authorize SSH Host
RUN mkdir -p /root/.ssh
COPY ./credentials/id_rsa /root/.ssh
RUN chmod 0700 /root/.ssh && \
    ssh-keyscan github.com > /root/.ssh/known_hosts && \
    chmod 600 /root/.ssh/id_rsa

RUN pip3 install git+ssh://git@github.com/ECHOESProj/eo-io@main#egg=eo-io

COPY ./credentials/config_eo_service.yml /root/config_eo_service.yml


COPY ./eoian /app/eoian
WORKDIR /app/

ENTRYPOINT  [ "python3", "-W", "ignore", "-m", "eoian" ]
