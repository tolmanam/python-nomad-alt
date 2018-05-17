import nomad_alt
import nomad_alt.exceptions
from nomad_alt.base import CB
from json import dumps, loads

class Jobs(object):
    """"""

    def __init__(self, agent):
        self.agent = agent

    def __contains__(self, item):

        try:
            j = self.read(item)
            return True
        except nomad_alt.exceptions.NomadException:
            return False

    def __getitem__(self, item):

        try:
            j = self.read(item)
            return j
        except nomad_alt.exceptions.NomadException:
            raise KeyError

    def list(self, prefix=None):
        """This endpoint lists all known jobs in the system registered with Nomad.

        :param prefix (string: "") - Specifies a string to filter jobs on based on an index prefix. This is specified as a querystring parameter.

        :return application/json
"""
        params = {}
        if prefix is not None:
            params['prefix'] = prefix
        return self.agent.http.get(
            CB.json(index=False, decode='Payload', allow_404=False),
            '/v1/jobs', params=params)

    def create(self, job_dict, **kwargs):
        """This endpoint creates (aka "registers") a new job in the system.

        :param Job (Job: <required>) - Specifies the JSON definition of the job.
        :param EnforceIndex (bool: false) - If set, the job will only be registered if the passed JobModifyIndex matches
            the current job's index. If the index is zero, the register only occurs if the job is new. This paradigm
            allows check-and-set style job updating.
        :param JobModifyIndex (int: 0) - Specifies the JobModifyIndex to enforce the current job is at.
        :param PolicyOverride (bool: false) - If set, any soft mandatory Sentinel policies will be overridden. This
            allows a job to be registered when it would be denied by policy.

        :return application/json
"""
        path = '/v1/jobs'
        params = kwargs
        data = dumps(job_dict)
        return self.agent.http.post(
            CB.json(), path, params=params, data=data)

    def read(self, job_id):
        """This endpoint reads information about a single job for its specification and status.

        :param job_id (string: <required>) - Specifies the ID of the job (as specified in the job file during submission). This is specified as part of the path.

        :return application/json
"""
        return self.agent.http.get(
            CB.json(index=False, allow_404=False),
            '/v1/job/%s' % job_id)

    def versions(self, job_id):
        """This endpoint reads information about all versions of a job.

:job_id (string: <required>) - Specifies the ID of the job (as specified in the job file during submission). This is specified as part of the path.

        :return application/json
"""
        return self.agent.http.get(
            CB.json(index=False, allow_404=False),
            '/v1/job/%s/versions' % job_id)

    def allocations(self, job_id, all=False):
        """This endpoint reads information about a single job's allocations.

:job_id (string: <required>) - Specifies the ID of the job (as specified in the job file during submission). This is specified as part of the path.

all (bool: false) - Specifies whether the list of allocations should include allocations from a previously registered job with the same ID. This is possible if the job is deregistered and reregistered.

        :return application/json
"""
        params = {'all': all}
        return self.agent.http.get(
            CB.json(index=False, allow_404=False),
            '/v1/job/%s/allocations' % job_id, params=params)

    def evaluations(self, job_id):
        """This endpoint reads information about a single job's evaluations

:job_id (string: <required>) - Specifies the ID of the job (as specified in the job file during submission). This is specified as part of the path.

        :return application/json
"""
        return self.agent.http.get(
            CB.json(index=False, allow_404=False),
            '/v1/job/%s/evaluations' % job_id)

    def deployments(self, job_id):
        """This endpoint lists a single job's deployments

:job_id (string: <required>) - Specifies the ID of the job (as specified in the job file during submission). This is specified as part of the path.

        :return application/json
"""
        return self.agent.http.get(
            CB.json(index=False, allow_404=False),
            '/v1/job/%s/deployments' % job_id)

    def most_recent_deployment(self, job_id):
        """This endpoint returns a single job's most recent deployment.

:job_id (string: <required>) - Specifies the ID of the job (as specified in the job file during submission). This is specified as part of the path.

        :return application/json
"""
        return self.agent.http.get(
            CB.json(index=False, allow_404=False),
            '/v1/job/%s/deployment' % job_id)

    def summary(self, job_id):
        """This endpoint reads summary information about a job.

:job_id (string: <required>) - Specifies the ID of the job (as specified in the job file during submission). This is specified as part of the path.

        :return application/json
"""
        return self.agent.http.get(
            CB.json(index=False, allow_404=False),
            '/v1/job/%s/summary' % job_id)

    def update(self, job_id, job_dict, **kwargs):
        """This endpoint registers a new job or updates an existing job.

:job_id (string: <required>) - Specifies the ID of the job (as specified in the job file during submission). This is specified as part of the path.

:json_job (JSON Job: <required>) - Specifies the JSON definition of the job.

:EnforceIndex (bool: false) - If set, the job will only be registered if the passed JobModifyIndex matches the current job's index. If the index is zero, the register only occurs if the job is new. This paradigm allows check-and-set style job updating.

:JobModifyIndex (int: 0) - Specifies the JobModifyIndex to enforce the current job is at.

:PolicyOverride (bool: false) - If set, any soft mandatory Sentinel policies will be overridden. This allows a job to be registered when it would be denied by policy.

        :return application/json
"""
        params = kwargs
        params.update(job_dict)
        return self.agent.http.post(
            CB.json(index=False, allow_404=False),
            '/v1/job/%s' % job_id, data=dumps(params))

    def dispatch(self, job_id, **kwargs):
        """This endpoint dispatches a new instance of a parameterized job.

        :return application/json
"""
        return self.agent.http.post(
            CB.json(index=False, allow_404=False),
            '/v1/job/%s/dispatch' % job_id, data=kwargs)

    # TODO - I don't think this is working yet
    def revert(self, job_id, version=0, prior=None, **kwargs):
        """This endpoint reverts the job to an older version.

        :param JobID (string: <required>) - Specifies the ID of the job (as specified in the job file during submission). This is specified as part of the path.
        :param JobVersion (integer: 0) - Specifies the job version to revert to.
        :param EnforcePriorVersion (integer: nil) - Optional value specifying the current job's version. This is checked and acts as a check-and-set value before reverting to the specified job.

        :return application/json
"""
        params = kwargs
        params['JobID'] = job_id
        params['JobVersion'] = version
        if prior is not None:
            params['EnforcePriorVersion'] = prior

        return self.agent.http.post(
            CB.json(index=False, allow_404=False),
            '/v1/job/%s/revert' % job_id, data=dumps(params))

    # TODO - I don't think this is working yet
    def stability(self, job_id, version=0, stable=False, **kwargs):
        """This endpoint sets the job's stability.

        :param job_id (string: <required>) - Specifies the ID of the job (as specified in the job file during submission). This is specified as part of the path.
        :param version (integer: 0) - Specifies the job version to set the stability on.
        :param stable (bool: false) - Specifies whether the job should be marked as stable or not.

        :return application/json
"""
        params = kwargs
        params['JobID'] = job_id
        params['Job'] = {'ID': job_id}
        params['JobVersion'] = version
        params['Stable'] = stable

        return self.agent.http.post(
            CB.json(index=False, allow_404=False),
            '/v1/job/%s/stability' % job_id, data=dumps(params))

    def evaluate(self, job_id):
        """This endpoint creates a new evaluation for the given job. This can be used to force run the scheduling logic if necessary.

        :return application/json
"""
        return self.agent.http.post(
            CB.json(index=False, allow_404=False),
            '/v1/job/%s/evaluate' % job_id)

    def plan(self, job_id, job_dict, **kwargs):
        """This endpoint invokes a dry-run of the scheduler for the job.


Parameters
:job_id (string: <required>) - Specifies the ID of the job (as specified in
the job file during submission). This is specified as part of the path.

Job (string: <required>) - Specifies the JSON definition of the job.

Diff (bool: false) - Specifies whether the diff structure between the submitted and server side version of the job should be included in the response.

PolicyOverride (bool: false) - If set, any soft mandatory Sentinel policies will be overridden. This allows a job to be registered when it would be denied by policy.

        :return application/json
"""
        params = kwargs
        params.update(job_dict)

        return self.agent.http.post(
            CB.json(index=False),
            '/v1/job/%s/plan' % job_id, data=dumps(params))

    def force_periodic(self, job_id):
        """This endpoint forces a new instance of the periodic job. A new instance will be created even if it violates the job's prohibit_overlap settings. As such, this should be only used to immediately run a periodic job.

        :return application/json
"""
        return self.agent.http.post(
            CB.json(index=False),
            '/v1/job/%s/periodic/force' % job_id)

    def stop(self, job_id, **kwargs):
        """This endpoint deregisters a job, and stops all allocations part of it.

:job_id (string: <required>) - Specifies the ID of the job (as specified in the job file during submission). This is specified as part of the path.

:Purge (bool: false) - Specifies that the job should stopped and purged immediately. This means the job will not be queryable after being stopped. If not set, the job will be purged by the garbage collector.

        :return application/json
"""
        params = kwargs
        return self.agent.http.delete(
            CB.json(), '/v1/job/%s' % job_id, params=params)
