===========
Credentials
===========

The following is an example configuration file for CREODIAS (with dummy credentials):

.. code-block:: javascript

    creodias:
        priority: 5 # Lower value means lower priority (Default: 0)
        search:   # Search parameters configuration
        download:
            extract:
            outputs_prefix: /data/
        auth:
            credentials:
                username: licensing@example.com
                password: 170vk5aqtaus
        storage:
            region_name: null
            endpoint_url_local: http://data.cloudferro.com
            endpoint_url_ext: https://cf2.cloudferro.com:8080
            aws_access_key_id: 4u19ibpo18n8rb3ur2awi4glspt6c001
            aws_secret_access_key: jv27r8x005pz03uwmvb0zy9ajqfmupr5
            config: null
            output_directory: /data/
            bucket: compass-eo


The ``priority``, ``search``, ``download`` and auth ``parameters`` are passed to EODAG (see `EODAD configuration documentation <https://eodag.readthedocs.io/en/stable/getting_started_guide/configure.html>`_).

The endpoint https://cf2.cloudferro.com:8080 is for the object store containing the >20 PB of EO stored on CREODIAS. The http://data.cloudferro.com endpoint is of the read/write object store, used for storing the files created from the processing (see :ref:`Object Store`).