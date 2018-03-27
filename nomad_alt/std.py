import logging

import requests

from nomad_alt import base
from nomad_alt.base import HTTPClient as HTTPClient_base

__all__ = ['Nomad']


class HTTPClient(HTTPClient_base):
    def __init__(self, *args, **kwargs):
        super(HTTPClient, self).__init__(*args, **kwargs)
        self.session = requests.session()

    def response(self, response):
        response.encoding = 'utf-8'
        return base.Response(
            response.status_code, response.headers, response.text)

    def get(self, callback, path, params=None):
        uri = self.uri(path, params)
        return callback(self.response(
            self.session.get(uri, headers={"X-Nomad-Token": self.token}, verify=self.verify, cert=self.cert)))

    def put(self, callback, path, params=None, data=''):
        uri = self.uri(path, params)
        return callback(self.response(
            self.session.put(uri, data=data, verify=self.verify,
                             cert=self.cert, headers={"X-Nomad-Token": self.token})))

    def delete(self, callback, path, params=None):
        uri = self.uri(path, params)
        return callback(self.response(
            self.session.delete(uri, verify=self.verify, headers={"X-Nomad-Token": self.token}, cert=self.cert)))

    def post(self, callback, path, params=None, data=''):
        uri = self.uri(path, params)
        logging.warn("Post to %s", uri)
        return callback(self.response(
            self.session.post(uri, data=data, headers={"X-Nomad-Token": self.token}, verify=self.verify,
                              cert=self.cert)))


class Nomad(base.Nomad):
    def connect(self, host, port, scheme, verify=True, cert=None, token=None):
        return HTTPClient(host, port, scheme, verify, cert, token=token)
