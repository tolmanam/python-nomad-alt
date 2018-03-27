import nomad_alt
import nomad_alt.exceptions
from nomad_alt.base import CB
from json import dumps, loads

class Metrics(object):

    def __init__(self, agent):
        self.agent = agent

    def fetch(self, format=None):
        """The /metrics endpoint returns metrics for the current Nomad process.

        :param format (string: "") - Specifies the metrics format to be other than the JSON default. Currently, only prometheus is supported as an alterntaive format. This is specified as a querystring parameter.

        :return application/json
"""
        params = {}
        if format is not None:
            params['format'] = format
        return self.agent.http.get(
            CB.json(index=False, allow_404=False),
            '/v1/metrics', params=params)
