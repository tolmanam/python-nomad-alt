import nomad_alt
import nomad_alt.exceptions
from nomad_alt.base import CB
from json import dumps, loads
""" Agent HTTP API

The /agent endpoints are used to interact with the local Nomad agent.
"""

class Agent(object):

    def __init__(self, agent):
        self.agent = agent

    def members(self):
        """This endpoint queries the agent for the known peers in the gossip pool. This endpoint is only applicable to servers. Due to the nature of gossip, this is eventually consistent.

        :return application/json
"""
        return self.agent.http.get(
            CB.json(index=False, allow_404=False),
            '/v1/agent/members')

    def servers(self):
        """This endpoint lists the known server nodes. The servers endpoint is used to query an agent in client mode for its list of known servers. Client nodes register themselves with these server addresses so that they may dequeue work. The servers endpoint can be used to keep this configuration up to date if there are changes in the cluster.

        :return application/json
"""
        return self.agent.http.get(
            CB.json(index=False, allow_404=False),
            '/v1/agent/servers')

    def replace_servers(self, address):
        """This endpoint updates the list of known servers to the provided list. This replaces all previous server addresses with the new list.

        :param: address (string|list of strings: <required>) - Specifies the list of addresses in the format ip:port.

        :return Boolean
"""
        if isinstance(address, list):
            address = [('address', a) for a in address]
        else:
            address = [('address', address)]
        return self.agent.http.post(
            CB.bool(),
            '/v1/agent/servers', params=address)

    def state(self):
        """This endpoint queries the state of the target agent (self).

        :return:
        """
        return self.agent.http.get(
            CB.json(index=False, allow_404=False),
            '/v1/agent/self')