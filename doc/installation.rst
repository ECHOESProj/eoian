============
Installation
============


Clone the repository
--------------------

.. code-block:: console

    $ git clone https://github.com/ECHOESProj/eoian.git


Add the config files
--------------------

The configuration files contain the credentials for CREODIAS. These are stored in LastPass in folder/name: Shared-ECHOES/"eoian configuration files". Download them and store them in eoian/config (see :ref:`Credentials`).


Install with PIP
----------------

The code has been tested on Ubuntu 20.04.

Firstly, install the required libraries with:

.. code-block:: console

    $ apt-get install -y python3-pip binutils netcdf-bin libproj-dev gdal-bin libnetcdf-dev libhdf5-serial-dev libproj-dev libgeos-dev proj-data proj-bin

It is recommend to install the Python packages into a virtual environment. Install the Python packages with:

.. code-block:: console

    $  pip3 install -r requirements.txt