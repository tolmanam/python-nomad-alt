from json import dumps

from nomad_alt.base import CB


class Deployments(object):
    """The /deployment endpoints are used to query for and interact with deployments."""

    def __init__(self, agent):
        self.agent = agent

    def list(self, prefix=None):
        """This endpoint lists all deployments

:param: prefix (string: "")- Specifies a string to filter deployments on based on an index prefix. This is specified as a querystring parameter
"""
        params = {}
        if prefix is not None:
            params['prefix'] = prefix
        return self.agent.http.get(
            CB.json(index=False, decode='Payload'),
            '/v1/deployments', params=params)

    def read(self, deployment_id):
        """This endpoint reads information about a specific deployment by ID.

:param: deployment_id (string: <required>)- Specifies the UUID of the deployment. This must be the full UUID, not the short 8-character one. This is specified as part of the path.

"""
        return self.agent.http.get(
            CB.json(index=False),
            '/v1/deployment/%s' % deployment_id)

    def allocations(self, deployment_id):
        """This endpoint lists the allocations created or modified for the given deployment.

:param: deployment_id (string: <required>)- Specifies the UUID of the deployment. This must be the full UUID, not the short 8-character one. This is specified as part of the path.

"""
        return self.agent.http.get(
            CB.json(index=False),
            '/v1/deployment/allocations/%s' % deployment_id)

    def fail(self, deployment_id):
        """This endpoint is used to mark a deployment as failed. This should be done to force the scheduler to stop creating allocations as part of the deployment or to cause a rollback to a previous job version. This endpoint only triggers a rollback if the most recent stable version of the job has a different specification than the job being reverted.

:param: deployment_id (string: <required>)- Specifies the UUID of the deployment. This must be the full UUID, not the short 8-character one. This is specified as part of the path.

"""
        return self.agent.http.post(
            CB.json(index=False),
            '/v1/deployment/fail/%s' % deployment_id)

    def pause(self, deployment_id, pause=False):
        """This endpoint is used to pause or unpause a deployment. This is done to pause a rolling upgrade or resume it.

:param: deployment_id (string: <required>)- Specifies the UUID of the deployment. This must be the full UUID, not the short 8-character one. This is specified as part of the path.
:param: Pause (bool: false) - Specifies whether to pause or resume the deployment.
"""
        req = {
            'DeploymentID': deployment_id,
            'Pause': True if pause else False
        }
        data = dumps(req)
        return self.agent.http.post(
            CB.json(index=False),
            '/v1/deployment/pause/%s' % deployment_id, data=data)

    def promote(self, deployment_id, all_vals=False, groups=None):
        """This endpoint is used to promote task groups that have canaries for a deployment. This should be done when the placed canaries are healthy and the rolling upgrade of the remaining allocations should begin.

:param: deployment_id (string: <required>)- Specifies the UUID of the deployment. This must be the full UUID, not the short 8-character one. This is specified as part of the path.
:param: all (bool: false) - Specifies whether all task groups should be promoted.
:param: groups (array<string>: nil) - Specifies a particular set of task groups that should be promoted.
"""
        req = {
            'DeploymentID': deployment_id,
        }
        if all_vals:
            req['All'] = True
        if groups:
            if isinstance(groups, list):
                req['Groups'] = groups
            else:
                raise RuntimeError("When calling promote, the 'groups' argument must be a list if provided")
        data = dumps(req)
        return self.agent.http.post(
            CB.json(index=False),
            '/v1/deployment/promote/%s' % deployment_id, data=data)

    def allocation_health(self, deployment_id, HealthyAllocationIDs=None, UnhealthyAllocationIDs=None):
        """This endpoint is used to promote task groups that have canaries for a deployment. This should be done when the placed canaries are healthy and the rolling upgrade of the remaining allocations should begin.

:param: deployment_id (string: <required>)- Specifies the UUID of the deployment. This must be the full UUID, not the short 8-character one. This is specified as part of the path.
:param: all (bool: false) - Specifies whether all task groups should be promoted.
:param: groups (array<string>: nil) - Specifies a particular set of task groups that should be promoted.
"""
        req = {
            'DeploymentID': deployment_id,
        }
        if HealthyAllocationIDs:
            if isinstance(HealthyAllocationIDs, list):
                req['HealthyAllocationIDs'] = HealthyAllocationIDs
            else:
                raise RuntimeError("When calling promote, the 'HealthyAllocationIDs' argument must be a list if provided")
        if UnhealthyAllocationIDs:
            if isinstance(UnhealthyAllocationIDs, list):
                req['UnhealthyAllocationIDs'] = UnhealthyAllocationIDs
            else:
                raise RuntimeError("When calling promote, the 'UnhealthyAllocationIDs' argument must be a list if provided")
        data = dumps(req)
        return self.agent.http.post(
            CB.json(index=False),
            '/v1/deployment/allocation-health/%s' % deployment_id, data=data)
