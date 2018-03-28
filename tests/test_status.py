import logging

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

def test_leader(nomad_setup):
    res = nomad_setup.status.leader()
    logging.warn("Leader: %s", pformat(res))
    print("Leader: %s" % pformat(res))
    assert res is not None

def test_peers(nomad_setup):
    res = nomad_setup.status.peers()
    logging.warn("Peers: %s", pformat(res))
    print("Peers: %s" % pformat(res))
    assert res is not None
    assert isinstance(res, list)
