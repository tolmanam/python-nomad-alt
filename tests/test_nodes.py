import json
import logging
import uuid

import os
from pprint import pformat

import pytest

from nomad_alt import Nomad

import nomad_alt.exceptions
import tests.common as common


@pytest.fixture
def nomad_setup():
    n = Nomad(host=common.IP, port=common.NOMAD_PORT, ssl_verify=False, token=common.NOMAD_TOKEN)
    with open(common.EXAMPLE_JOB_JSON) as fh:
        n.jobs.create(json.loads(fh.read()))
    yield n
    n.jobs.stop(common.EXAMPLE_JOB_NAME, purge=True)


# integration tests requires nomad Vagrant VM or Binary running
def test_get_nodes(nomad_setup):
    res = nomad_setup.nodes.list()
    assert isinstance(res, list) == True
    for node in res:
        node_details = nomad_setup.nodes.read(node['ID'])
        assert isinstance(node_details, dict)
        assert node_details['ID'] == node['ID']
        node_allocations = nomad_setup.nodes.allocations(node['ID'])
        assert isinstance(node_allocations, list)
        node_eval = nomad_setup.nodes.evaluate(node['ID'])
        # logging.warn("Allocations:\n%s", pformat(node_eval))
        if node_eval is not None:
            assert isinstance(node_eval, dict)
