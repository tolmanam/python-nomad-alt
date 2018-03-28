import nomad_alt
import nomad_alt.exceptions
from nomad_alt.base import CB
from json import dumps, loads


class Status(object):
    """
The /status endpoints query the Nomad system status.
    """
    def __init__(self, agent):
        self.agent = agent

    def leader(self):
        """This endpoint returns the address of the current leader in the region.

        :return application/json
"""
        return self.agent.http.get(
            CB.json(index=False, allow_404=False),
            '/v1/status/leader')

    def peers(self):
        """This endpoint returns the set of raft peers in the region.

        :return application/json
"""
        return self.agent.http.get(
            CB.json(index=False, allow_404=False),
            '/v1/status/peers')
