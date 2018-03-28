import nomad_alt
import nomad_alt.exceptions
from nomad_alt.base import CB
from json import dumps, loads

class Client(object):
    """"""

    def __init__(self, agent):
        self.agent = agent

    def stats(self):
        """This endpoint queries the actual resources consumed on a node. The API endpoint is hosted by the Nomad client and requests have to be made to the nomad client whose resource usage metrics are of interest.

        :return application/json
"""
        return self.agent.http.get(
            CB.json(index=False, allow_404=False),
            '/v1/client/stats')

    def allocation(self, alloc_id):
        """This endpoint queries the actual resources consumed on a node. The API endpoint is hosted by the Nomad client and requests have to be made to the nomad client whose resource usage metrics are of interest.

        :param: :alloc_id (string: <required>) - Specifies the allocation ID to query. This is specified as part of the URL. Note, this must be the full allocation ID, not the short 8-character one. This is specified as part of the path.

        :return application/json
"""
        return self.agent.http.get(
            CB.json(index=False, allow_404=False),
            '/v1/client/allocation/%s/stats' % alloc_id)
