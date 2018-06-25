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
        logging.warning("Get from %s using %s", uri, self.cert)
        return callback(self.response(
            self.session.get(uri,
                             headers={"X-Nomad-Token": self.token},
                             verify=self.verify,
                             cert=self.cert if self.key is None else (self.cert, self.key)
                             )))

    def put(self, callback, path, params=None, data=''):
        uri = self.uri(path, params)
        logging.warning("Put to %s", uri)
        return callback(self.response(
            self.session.put(uri,
                             data=data,
                             headers={"X-Nomad-Token": self.token},
                             verify=self.verify,
                             cert=self.cert if self.key is None else (self.cert, self.key)
                             )))

    def delete(self, callback, path, params=None):
        uri = self.uri(path, params)
        logging.warning("delete from %s", uri)
        return callback(self.response(
            self.session.delete(uri,
                                headers={"X-Nomad-Token": self.token},
                                verify=self.verify,
                                cert=self.cert if self.key is None else (self.cert, self.key)
                                )))

    def post(self, callback, path, params=None, data=''):
        uri = self.uri(path, params)
        logging.warning("Post to %s", uri)
        return callback(self.response(
            self.session.post(uri,
                              data=data,
                              headers={"X-Nomad-Token": self.token},
                              verify=self.verify,
                              cert=self.cert if self.key is None else (self.cert, self.key)
                              )))


class Nomad(base.Nomad):
    def connect(self, host, port, scheme, verify=True, cert=None, token=None, key=None, ca=None):
        return HTTPClient(host, port, scheme, verify, cert, token=token, key=key, ca=ca)
