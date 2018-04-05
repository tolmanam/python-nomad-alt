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

def test_allocation_list(nomad_setup):
    res = nomad_setup.allocations.list()
    assert len(res) > 0
    assert common.EXAMPLE_JOB_NAME in [a['JobID'] for a in res]

    alloc_id = res[0]['ID']
    res = nomad_setup.allocations.list(alloc_id[:6])
    assert len(res) > 0

    fake_alloc = "%s" % uuid.uuid4()
    res = nomad_setup.allocations.list(fake_alloc[:6])
    assert len(res) == 0

    res = nomad_setup.allocations.read(alloc_id)
    assert 'JobID' in res
    assert 'ModifyIndex' in res

# def test_allocation_read(nomad_setup):
#     assert len(nomad_setup.allocations.read()) > 0
