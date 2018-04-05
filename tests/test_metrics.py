from nomad_alt import Nomad
import json
import uuid

from pprint import pformat
import os
import pytest
import nomad_alt.exceptions
import tests.common as common


@pytest.fixture
def nomad_setup():
    n = Nomad(host=common.IP, port=common.NOMAD_PORT, ssl_verify=False, token=common.NOMAD_TOKEN)
    with open(common.EXAMPLE_JOB_JSON) as fh:
        n.jobs.create(json.loads(fh.read()))
    yield n
    n.jobs.stop(common.EXAMPLE_JOB_NAME, purge=True)

def test_metrics(nomad_setup):
    res = nomad_setup.metrics.fetch()
    assert res is not None
    assert 'Counters' in res
    assert 'Gauges' in res
    assert 'Points' in res
    assert 'Samples' in res
    assert 'Timestamp' in res
