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
    n = Nomad(host=common.IP, port=common.NOMAD_PORT, verify=False, token=common.NOMAD_TOKEN)
    with open(common.EXAMPLE_JOB_JSON) as fh:
        n.jobs.create(json.loads(fh.read()))
    yield n
    n.jobs.stop(common.EXAMPLE_JOB_NAME, purge=True)

def test_allocation_list(nomad_setup):
    res = nomad_setup.allocations.list()
    print "Allocation:\n%s" % pformat(res)
    assert len(res) > 0
    assert False

# def test_allocation_read(nomad_setup):
#     assert len(nomad_setup.allocations.read()) > 0
