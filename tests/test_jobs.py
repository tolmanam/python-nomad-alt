import json
import uuid

import os
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
def test_get_jobs(nomad_setup):
    assert isinstance(nomad_setup.jobs.list(), list) == True


def test_register_job(nomad_setup):
    with open(common.EXAMPLE_JOB_JSON) as fh:
        job_id = "%s" % uuid.uuid4()
        job_example = json.loads(fh.read())
        job_example['Job']['ID'] = job_id
        job_example['Job']['Name'] = job_id
        nomad_setup.jobs.create(job_example)

        assert job_id in [job['ID'] for job in nomad_setup.jobs.list()]

        assert len([job['ID'] for job in nomad_setup.jobs.list(prefix=job_id)]) == 1
        assert len([job['ID'] for job in nomad_setup.jobs.list(prefix=job_id[:-3])]) == 1

        nomad_setup.jobs.stop(job_id, purge=True)
        assert job_id not in [job['ID'] for job in nomad_setup.jobs.list()]


def test_get_reference_job_as_list(nomad_setup):
        j = nomad_setup.jobs[common.EXAMPLE_JOB_NAME]
        assert isinstance(j, dict)
        assert j["ID"] == common.EXAMPLE_JOB_NAME

        assert common.EXAMPLE_JOB_NAME in nomad_setup.jobs

        with pytest.raises(KeyError):
            j = nomad_setup.jobs["%s" % uuid.uuid4()]

        assert "%s" % uuid.uuid4() not in nomad_setup.jobs

def test_get_job(nomad_setup):
    assert isinstance(nomad_setup.jobs[common.EXAMPLE_JOB_NAME], dict) == True


def test_get_allocations(nomad_setup):
    j = nomad_setup.jobs[common.EXAMPLE_JOB_NAME]
    a = nomad_setup.jobs.allocations(common.EXAMPLE_JOB_NAME)
    assert j["ID"] == a[0]["JobID"]


def test_get_evaluations(nomad_setup):
    j = nomad_setup.jobs[common.EXAMPLE_JOB_NAME]
    e = nomad_setup.jobs.evaluations(common.EXAMPLE_JOB_NAME)
    assert j["ID"] == e[0]["JobID"]


def test_evaluate_job(nomad_setup):
    assert "EvalID" in nomad_setup.jobs.evaluate(common.EXAMPLE_JOB_NAME)

# # def test_periodic_job(nomad_setup):
# #     assert "EvalID" in nomad_setup.jobs.periodic_job(common.EXAMPLE_JOB_NAME)


# def test_delete_job(nomad_setup):
#     assert "EvalID" in nomad_setup.jobs.deregister_job(common.EXAMPLE_JOB_NAME)
#     test_register_job(nomad_setup)


# @pytest.mark.skipif(tuple(int(i) for i in os.environ.get("NOMAD_VERSION").split(".")) < (0, 5, 3), reason="Nomad dispatch not supported")
# def test_dispatch_job(nomad_setup):
#     with open("example_batch_parameterized.json") as fh:
#         job = json.loads(fh.read())
#         nomad_setup.jobs.register_job("example-batch", job)
#     try:
#         nomad_setup.jobs.dispatch_job("example-batch", meta={"time": "500"})
#     except (exceptions.URLNotFoundNomadException,
#             exceptions.BaseNomadException) as e:
#         print(e.nomad_resp.text)
#         raise e
#     assert "example-batch" in nomad_setup.job


def test_summary_job(nomad_setup):
    s = nomad_setup.jobs.summary(common.EXAMPLE_JOB_NAME)
    """ TODO: There are more checks that we could do here"""
    assert "JobID" in s
    assert "ModifyIndex" in s
    assert "Namespace" in s
    assert "Summary" in s
    assert "Children" in s
    assert "Running" in s['Children']


def test_plan_new_job(nomad_setup):
    with open(common.EXAMPLE_JOB_JSON) as fh:
        job_id = "%s" % uuid.uuid4()
        job_example = json.loads(fh.read())
        job_example['Job']['ID'] = job_id
        job_example['Job']['Name'] = job_id
        if "Meta" not in job_example['Job'] or not isinstance(job_example['Job']['Meta'], dict):
            job_example['Job']['Meta'] = {}
        job_example['Job']['Meta']['bogus'] = "%s" % uuid.uuid4()
        p = nomad_setup.jobs.plan(job_id, job_example)
        assert "Index" in p
        assert p["Index"] == 0
        assert "JobModifyIndex" in p
        assert p["JobModifyIndex"] == 0


def test_plan_existing_job(nomad_setup):
    with open(common.EXAMPLE_JOB_JSON) as fh:
        job_example = json.loads(fh.read())
        p = nomad_setup.jobs.plan(common.EXAMPLE_JOB_NAME, job_example)
        assert "Index" in p
        assert p["Index"] > 0
        assert "JobModifyIndex" in p
        assert p["JobModifyIndex"] > 0

def test_versions_job(nomad_setup):
    assert "Versions" in nomad_setup.jobs.versions(common.EXAMPLE_JOB_NAME)

def test_versions_job_missing(nomad_setup):
    with pytest.raises(nomad_alt.exceptions.NomadException):
        assert "Versions" in nomad_setup.jobs.versions("%s" % uuid.uuid4())

def test_get_job_deployments(nomad_setup):
    assert isinstance(nomad_setup.jobs.deployments(common.EXAMPLE_JOB_NAME), list)
    assert isinstance(nomad_setup.jobs.deployments(common.EXAMPLE_JOB_NAME)[0], dict)
    assert "JobID" in nomad_setup.jobs.deployments(common.EXAMPLE_JOB_NAME)[0]
    assert common.EXAMPLE_JOB_NAME == nomad_setup.jobs.deployments(common.EXAMPLE_JOB_NAME)[0]["JobID"]

def test_get_job_most_recent_deployment(nomad_setup):
    assert isinstance(nomad_setup.jobs.most_recent_deployment(common.EXAMPLE_JOB_NAME), dict)
    assert "JobID" in nomad_setup.jobs.most_recent_deployment(common.EXAMPLE_JOB_NAME)
    assert common.EXAMPLE_JOB_NAME == nomad_setup.jobs.most_recent_deployment(common.EXAMPLE_JOB_NAME)["JobID"]

def test_get_job_summary(nomad_setup):
    assert isinstance(nomad_setup.jobs.summary(common.EXAMPLE_JOB_NAME), dict)
    assert "JobID" in nomad_setup.jobs.summary(common.EXAMPLE_JOB_NAME)
    assert common.EXAMPLE_JOB_NAME == nomad_setup.jobs.summary(common.EXAMPLE_JOB_NAME)["JobID"]

def test_update_job(nomad_setup):
    with open(common.EXAMPLE_JOB_JSON) as fh:
        job_example = json.loads(fh.read())
        job_example['Job']['TaskGroups'][0]['Name'] = "%s" % uuid.uuid4()
        p = nomad_setup.jobs.update(common.EXAMPLE_JOB_NAME, job_example)

@pytest.mark.skip
def test_revert_job(nomad_setup):

    """Can't seem to get this to work as expected.  The job version increases when I had expected it to drop back"""

    with open(common.EXAMPLE_JOB_JSON) as fh:
        job_example = json.loads(fh.read())
        for i in range(1,5):
            job_example['Job']['TaskGroups'][0]['Name'] = "%s" % uuid.uuid4()
            p = nomad_setup.jobs.update(common.EXAMPLE_JOB_NAME, job_example)

    print "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
    s = nomad_setup.jobs.summary(common.EXAMPLE_JOB_NAME)
    print s
    print nomad_setup.jobs.most_recent_deployment(common.EXAMPLE_JOB_NAME)

    current_job_version = nomad_setup.jobs.most_recent_deployment(common.EXAMPLE_JOB_NAME)["JobVersion"]
    prior_job_version = current_job_version - 1
    t = nomad_setup.jobs.revert(common.EXAMPLE_JOB_NAME, prior_job_version)
    # t = nomad_setup.jobs.revert(common.EXAMPLE_JOB_NAME, prior_job_version, current_job_version)

    print "--------------------------------------------------------------------------------"
    print t
    print "--------------------------------------------------------------------------------"

    s = nomad_setup.jobs.summary(common.EXAMPLE_JOB_NAME)
    print s
    print nomad_setup.jobs.most_recent_deployment(common.EXAMPLE_JOB_NAME)
    print "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"

    new_version = nomad_setup.jobs.most_recent_deployment(common.EXAMPLE_JOB_NAME)["JobVersion"]
    assert new_version == prior_job_version

@pytest.mark.skip
def test_stable_job(nomad_setup):

    with open(common.EXAMPLE_JOB_JSON) as fh:
        job_example = json.loads(fh.read())
        for i in range(1,5):
            job_example['Job']['TaskGroups'][0]['Name'] = "%s" % uuid.uuid4()
            p = nomad_setup.jobs.update(common.EXAMPLE_JOB_NAME, job_example)

    current_job_version = nomad_setup.jobs.most_recent_deployment(common.EXAMPLE_JOB_NAME)["JobVersion"]
    nomad_setup.jobs.stability(common.EXAMPLE_JOB_NAME, version=current_job_version, stable=True)
