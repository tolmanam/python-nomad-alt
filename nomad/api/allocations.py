from nomad.base import CB


class Allocations(object):
    """"""
    def __init__(self, agent):
        self.agent = agent

    def list(self, prefix=None):
        """The /allocation endpoints are used to query for and interact with allocations.

prefix (string: "")- Specifies a string to filter allocations on based on an index prefix. This is specified as a querystring parameter.
"""
        params = {}
        if prefix is not None:
            params['prefix'] = prefix
        return self.agent.http.get(
            CB.json(index=True, decode='Payload'),
            '/v1/allocations', params=params)

    def read(self, alloc_id):
        """
"""
        return self.agent.http.get(
            CB.json(index=True),
            '/v1/allocation/%s' % alloc_id)
