import pytest
import os
import urllib
from eoian.core.platforms import platform_config


def test_creodias():
    os.environ['DATA_SOURCE'] = 'creodias'
    assert platform_config().platform == 'creodias'
    del os.environ['DATA_SOURCE']


def test_peps():
    os.environ['DATA_SOURCE'] = 'peps'
    assert platform_config().platform == 'peps'
    del os.environ['DATA_SOURCE']


def test_store():
    os.environ['DATA_SOURCE'] = 'peps'
    assert platform_config().platform == 'peps'
    del os.environ['DATA_SOURCE']


def test_store_exists():
    plat = platform_config()
    try:
        status = urllib.request.urlopen(plat.endpoint_url_local, timeout=2).status == 200
    except urllib.error.HTTPError:
        status = True
    assert status
