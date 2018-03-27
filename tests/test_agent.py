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

def test_agent_members(nomad_setup):
    res = nomad_setup.agent.members()
    print res
    assert res is not None
    assert 'ServerName' in res
    assert 'ServerRegion' in res
    assert 'ServerDC' in res
    assert 'Members' in res

def test_agent_server(nomad_setup):
    server_list = nomad_setup.agent.servers()
    assert server_list is not None
    assert isinstance(server_list, list)

    fake_server_list = ['1.2.3.4:4647', '5.6.7.8:4647']
    assert nomad_setup.agent.replace_servers(fake_server_list)
    temp_svr_list = nomad_setup.agent.servers()
    assert len(temp_svr_list) == len(fake_server_list)

    assert nomad_setup.agent.replace_servers(fake_server_list[0])
    temp_svr_list = nomad_setup.agent.servers()
    assert len(temp_svr_list) == 1

    assert nomad_setup.agent.replace_servers(server_list)

def test_agent_state(nomad_setup):
    res = nomad_setup.agent.state()
    print pformat(res)
    assert res is not None
    assert isinstance(res, dict)
    assert 'config' in res
    assert 'stats' in res
