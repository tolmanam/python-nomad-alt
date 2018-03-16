from nomad_alt import Nomad
import json
import uuid

import os
import pytest
import nomad_alt.exceptions
import tests.common as common


@pytest.fixture
def nomad_setup():
    n = Nomad(host=common.IP, port=common.NOMAD_PORT, verify=False, token=common.NOMAD_TOKEN)
    if common.NOMAD_TOKEN is None:
        bootstrap_results = n.acl.bootstrap()
        common.NOMAD_TOKEN = bootstrap_results['SecretID']
    yield n

def test_acl_list(nomad_setup):
    if common.NOMAD_TOKEN:
        assert len(nomad_setup.acl.list()) > 0
        assert "Bootstrap Token" in [acl['Name'] for acl in nomad_setup.acl.list()]

def test_new_acl(nomad_setup):
    if common.NOMAD_TOKEN:
        acl_name = "%s" % uuid.uuid4()
        res = nomad_setup.acl.create('client', ["readonly"], name=acl_name)
        assert 'AccessorID' in res
        accessor_id = res['AccessorID']
        assert acl_name in [acl['Name'] for acl in nomad_setup.acl.list()]

        new_acl_name = "%s" % uuid.uuid4()
        nomad_setup.acl.update(accessor_id, 'client', ["readonly"], name=new_acl_name)
        assert new_acl_name in [acl['Name'] for acl in nomad_setup.acl.list()]

        res = nomad_setup.acl.read(accessor_id)
        assert 'AccessorID' in res
        assert accessor_id == res['AccessorID']
        assert 'Name' in res
        assert new_acl_name == res['Name']

        res = nomad_setup.acl.read()
        assert 'SecretID' in res
        assert common.NOMAD_TOKEN == res['SecretID']

        res = nomad_setup.acl.delete(accessor_id)
        assert new_acl_name not in [acl['Name'] for acl in nomad_setup.acl.list()]
