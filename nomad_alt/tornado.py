from __future__ import absolute_import

from tornado import gen
from tornado import httpclient

import nomad_alt
import nomad_alt.base
import nomad_alt.exceptions
from nomad_alt import base

__all__ = ['Nomad']


class HTTPClient(nomad_alt.base.HTTPClient):
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
        request = httpclient.HTTPRequest(uri, **kwargs)
        return self._request(callback, request)

    def get(self, callback, path, params=None):
        uri = self.uri(path, params)
        kwargs = {
            'method': 'GET',
            'validate_cert': self.verify,
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
    def connect(self, host, port, scheme, verify=True, cert=None, token=None):
        return HTTPClient(host, port, scheme, verify=verify, cert=cert, token=token)
