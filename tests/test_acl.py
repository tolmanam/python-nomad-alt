import logging
from pprint import pformat

from nomad_alt import Nomad
import json
import uuid

import os
import pytest
import nomad_alt.exceptions
import tests.common as common


@pytest.fixture
def nomad_setup():
    n = Nomad(host=common.IP, port=common.NOMAD_PORT, ssl_verify=False, token=common.NOMAD_TOKEN)
    if common.NOMAD_TOKEN is None:
        bootstrap_results = n.acl_tokens.bootstrap()
        common.NOMAD_TOKEN = bootstrap_results['SecretID']
    yield n

@pytest.mark.skip
def test_acl_token_list(nomad_setup):
    if common.NOMAD_TOKEN:
        assert len(nomad_setup.acl_tokens.list()) > 0
        assert "Bootstrap Token" in [acl['Name'] for acl in nomad_setup.acl_tokens.list()]

@pytest.mark.skip
def test_new_acl_token(nomad_setup):
    if common.NOMAD_TOKEN:
        acl_name = "%s" % uuid.uuid4()
        res = nomad_setup.acl_tokens.create('client', ["readonly"], name=acl_name)
        assert 'AccessorID' in res
        accessor_id = res['AccessorID']
        assert acl_name in [acl['Name'] for acl in nomad_setup.acl_tokens.list()]

        new_acl_name = "%s" % uuid.uuid4()
        nomad_setup.acl_tokens.update(accessor_id, 'client', ["readonly"], name=new_acl_name)
        assert new_acl_name in [acl['Name'] for acl in nomad_setup.acl_tokens.list()]

        res = nomad_setup.acl_tokens.read(accessor_id)
        assert 'AccessorID' in res
        assert accessor_id == res['AccessorID']
        assert 'Name' in res
        assert new_acl_name == res['Name']

        res = nomad_setup.acl_tokens.read()
        assert 'SecretID' in res
        assert common.NOMAD_TOKEN == res['SecretID']

        res = nomad_setup.acl_tokens.delete(accessor_id)
        assert new_acl_name not in [acl['Name'] for acl in nomad_setup.acl_tokens.list()]

@pytest.mark.skip
def test_acl_policies(nomad_setup):
    # create a example policy
    acl_policy_name = "%s" % uuid.uuid4()
    rules = ""
    res = nomad_setup.acl_policies.set(acl_policy_name, rules, description="%s" % uuid.uuid4())
    # logging.warn("res:%s", pformat(res))
    assert isinstance(res, bool)
    assert res

    # List policies
    res = nomad_setup.acl_policies.list()
    # logging.warn("res:%s", pformat(res))
    assert isinstance(res, list)
    assert acl_policy_name in [policy['Name'] for policy in res]

    # retrieve example policy
    res = nomad_setup.acl_policies.read(acl_policy_name)
    # logging.warn("res:%s", pformat(res))
    assert isinstance(res, dict)
    assert acl_policy_name == res['Name']

    # delete example policy
    res = nomad_setup.acl_policies.delete(acl_policy_name)
    # logging.warn("res:%s", pformat(res))
    assert isinstance(res, bool)
    assert res

    # retrieve example policy should not raise exception
    with pytest.raises(nomad_alt.exceptions.NomadException):
        res = nomad_setup.acl_policies.read(acl_policy_name)
