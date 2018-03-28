import nomad_alt
import nomad_alt.exceptions
from nomad_alt.base import CB
from json import dumps, loads

class Nodes(object):
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
        """This endpoint lists all nodes registered with Nomad.

        :param prefix (string: "") - Specifies a string to filter nodes on based on an index prefix. This is specified as a querystring parameter.

        :return application/json
"""
        params = {}
        if prefix is not None:
            params['prefix'] = prefix
        return self.agent.http.get(
            CB.json(index=False, decode='Payload', allow_404=False),
            '/v1/nodes', params=params)

    def read(self, node_id):
        """This endpoint reads information about a single job for its specification and status.

        :param :node_id (string: <required>)- Specifies the ID of the node. This must be the full UUID, not the short 8-character one. This is specified as part of the path.

        :return application/json
"""
        return self.agent.http.get(
            CB.json(index=False, allow_404=False),
            '/v1/node/%s' % node_id)

    def allocations(self, node_id):
        """This endpoint lists all of the allocations for the given node. This can be used to determine what allocations have been scheduled on the node, their current status, and the values of dynamically assigned resources, like ports.

        :param: :node_id (string: <required>)- Specifies the UUID of the node. This must be the full UUID, not the short 8-character one. This is specified as part of the path.

        :return application/json
"""
        return self.agent.http.get(
            CB.json(index=False, allow_404=False),
            '/v1/node/%s/allocations' % node_id)

    def evaluate(self, node_id):
        """This endpoint creates a new evaluation for the given node. This can be used to force a run of the scheduling logic.

        :param: :node_id (string: <required>)- Specifies the UUID of the node. This must be the full UUID, not the short 8-character one. This is specified as part of the path.

        :return application/json
"""
        return self.agent.http.get(
            CB.json(index=False, allow_404=False),
            '/v1/node/%s/evaluate' % node_id)

    def drain(self, node_id, enabled=True):
        """This endpoint toggles the drain mode of the node. When draining is enabled, no further allocations will be assigned to this node, and existing allocations will be migrated to new nodes.

        :param: :node_id (string: <required>)- Specifies the UUID of the node. This must be the full UUID, not the short 8-character one. This is specified as part of the path.
        :param: enable (bool: default True) - Specifies if drain mode should be enabled. This is specified as a query string parameter.

        :return application/json
"""
        params = {
            'enabled': 'true' if enabled else 'false'
        }
        return self.agent.http.post(
            CB.json(index=False, allow_404=False),
            '/v1/node/%s/drain' % node_id, params=params)

    def purge(self, node_id):
        """This endpoint purges a node from the system. Nodes can still join the cluster if they are alive.

        :param: :node_id (string: <required>)- Specifies the UUID of the node. This must be the full UUID, not the short 8-character one. This is specified as part of the path.

        :return application/json
"""
        return self.agent.http.post(
            CB.json(index=False, allow_404=False),
            '/v1/node/%s/purge' % node_id)
