from nomad_alt.base import CB


class Evaluations(object):
    """"""

    def __init__(self, agent):
        self.agent = agent

    def list(self, prefix=None):
        """The /evaluation endpoints are used to query for and interact with evaluations.

:prefix (string: "")- Specifies a string to filter evaluations on based on an index prefix. This is specified as a querystring parameter.
"""
        params = {}
        if prefix is not None:
            params['prefix'] = prefix
        return self.agent.http.get(
            CB.json(index=True, decode='Payload'),
            '/v1/evaluations', params=params)

    def read(self, eval_id):
        """This endpoint reads information about a specific evaluation by ID.
"""
        return self.agent.http.get(
            CB.json(index=True),
            '/v1/evaluation/%s' % eval_id)

    def allocations(self, eval_id):
        """

"""
        return self.agent.http.get(
            CB.json(index=True),
            '/v1/evaluation/%s/allocations' % eval_id)
