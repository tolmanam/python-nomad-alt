from __future__ import absolute_import
import logging

from tornado import gen
from tornado import httpclient

import nomad_alt
import nomad_alt.base
import nomad_alt.exceptions
from nomad_alt import base

__all__ = ['Nomad']

class HTTPClient(nomad_alt.base.HTTPClient):
    logger = logging.getLogger('nomad_alt.tornado.HTTPClient')
    def __init__(self, *args, **kwargs):
        super(HTTPClient, self).__init__(*args, **kwargs)
        self.client = httpclient.AsyncHTTPClient()

    def response(self, response):
        return base.Response(
            response.code, response.headers, response.body.decode('utf-8'))

    @gen.coroutine
    def _request(self, callback, request):
        try:
            response = yield self.client.fetch(request)
        except httpclient.HTTPError as e:
            if e.code == 599:
                raise nomad_alt.exceptions.Timeout
            response = e.response
        raise gen.Return(callback(self.response(response)))

    def __handle_request(self, callback, uri, kwargs):
        if not self.verify:
            kwargs['validate_cert'] = False
        else:
            kwargs['validate_cert'] = True
            kwargs['ca_certs'] = self.ca
            kwargs['client_cert'] = self.cert
            kwargs['client_key'] = self.key
        self.logger.debug("kwargs: %s", kwargs)
        request = httpclient.HTTPRequest(uri, **kwargs)
        return self._request(callback, request)

    def get(self, callback, path, params=None):
        uri = self.uri(path, params)
        kwargs = {
            'method': 'GET',
        }
        if self.token is not None:
            kwargs['headers'] = {"X-Nomad-Token": self.token}

        return self.__handle_request(callback, uri, kwargs)

    def put(self, callback, path, params=None, data=''):
        uri = self.uri(path, params)
        kwargs = {
            'method': 'PUT',
            'validate_cert': self.verify,
        }
        if self.token is not None:
            kwargs['headers'] = {"X-Nomad-Token": self.token}
        kwargs['body'] = '' if data is None else data

        return self.__handle_request(callback, uri, kwargs)

    def delete(self, callback, path, params=None):
        uri = self.uri(path, params)
        kwargs = {
            'method': 'DELETE',
            'validate_cert': self.verify,
        }
        if self.token is not None:
            kwargs['headers'] = {"X-Nomad-Token": self.token}

        return self.__handle_request(callback, uri, kwargs)

    def post(self, callback, path, params=None, data=''):
        uri = self.uri(path, params)
        kwargs = {
            'method': 'POST',
            'validate_cert': self.verify,
            'body': data
        }
        if self.token is not None:
            kwargs['headers'] = {"X-Nomad-Token": self.token}

        return self.__handle_request(callback, uri, kwargs)


class Nomad(base.Nomad):

    logger = logging.getLogger('nomad_alt.tornado.Nomad')

    def connect(self, host, port, scheme, verify=True, cert=None, token=None, key=None, ca=None):
        return HTTPClient(host, port, scheme, verify, cert, token=token, key=key, ca=ca)