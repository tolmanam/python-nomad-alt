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
    n = Nomad(host=common.IP, port=common.NOMAD_PORT, verify=False, token=common.NOMAD_TOKEN)
    with open(common.EXAMPLE_JOB_JSON) as fh:
        n.jobs.create(json.loads(fh.read()))
    yield n
    n.jobs.stop(common.EXAMPLE_JOB_NAME, purge=True)


def test_stats(nomad_setup):
    res = nomad_setup.client.stats()
    assert isinstance(res, dict)
    assert 'CPU' in res.keys()
    res = nomad_setup.nodes.list()
    assert isinstance(res, list) == True

    a = nomad_setup.jobs.allocations(common.EXAMPLE_JOB_NAME)
    node_alloc = a[0]

    logging.warn("Alloc:\n%s", node_alloc)
    node_details = nomad_setup.nodes.read(node_alloc['NodeID'])
    assert isinstance(node_details, dict)
    node_allocations = nomad_setup.nodes.allocations(node_alloc['NodeID'])
    for alloc in node_allocations:
        logging.warn("Node Allocation:\n%s", pformat(alloc))
        # alloc_stats = nomad_setup.client.allocation(alloc['ID'])
        # logging.warn("Allocations:\n%s", pformat(alloc_stats))
        # assert isinstance(alloc_stats, dict)

    for node in res:
        node_details = nomad_setup.nodes.read(node['ID'])
        # logging.warn("Node Details:\n%s", pformat(node_details))
        assert isinstance(node_details, dict)
        assert node_details['ID'] == node['ID']
        node_allocations = nomad_setup.nodes.allocations(node['ID'])
        # logging.warn("Node Allocations:\n%s", pformat(node_allocations))
        for alloc in node_allocations:
            alloc_stats = nomad_setup.client.allocation(alloc['ID'])
            # logging.warn("Allocations:\n%s", pformat(alloc_stats))
            assert isinstance(alloc_stats, dict)
