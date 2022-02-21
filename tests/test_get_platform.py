#  Copyright (c) 2022.
#  The ECHOES Project (https://echoesproj.eu/) / Compass Informatics

import pytest
import os
import urllib
from eoian.core.settings import configuration


def test_creodias():
    os.environ['DATA_SOURCE'] = 'creodias'
    assert configuration().config == 'creodias'
    del os.environ['DATA_SOURCE']


def test_peps():
    os.environ['DATA_SOURCE'] = 'peps'
    assert configuration().config == 'peps'
    del os.environ['DATA_SOURCE']


def test_store():
    os.environ['DATA_SOURCE'] = 'peps'
    assert configuration().config == 'peps'
    del os.environ['DATA_SOURCE']


def test_store_exists():
    plat = configuration()
    try:
        status = urllib.request.urlopen(plat.endpoint_url_local, timeout=2).status == 200
    except urllib.error.HTTPError:
        status = True
    assert status
