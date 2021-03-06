import abc
import base64
import collections
import json
from logging import getLogger
import os
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

import six
from six.moves import urllib

from nomad_alt.exceptions import NomadException, BadRequest, ACLDisabled, ACLPermissionDenied, NotFound



#
# Convenience to define checks

class Check(object):
    """
    There are three different kinds of checks: script, http and ttl
    """

    logger = getLogger(__name__)

    @classmethod
    def script(klass, script, interval):
        """
        Run *script* every *interval* (e.g. "10s") to peform health check
        """
        return {'script': script, 'interval': interval}

    @classmethod
    def http(klass, url, interval, timeout=None, deregister=None, header=None):
        """
        Peform a HTTP GET against *url* every *interval* (e.g. "10s") to peform
        health check with an optional *timeout* and optional *deregister* after
        which a failing service will be automatically deregistered. Optional
        parameter *header* specifies headers sent in HTTP request. *header*
        paramater is in form of map of lists of strings,
        e.g. {"x-foo": ["bar", "baz"]}.
        """
        ret = {'http': url, 'interval': interval}
        if timeout:
            ret['timeout'] = timeout
        if deregister:
            ret['DeregisterCriticalServiceAfter'] = deregister
        if header:
            ret['header'] = header
        return ret

    @classmethod
    def tcp(klass, host, port, interval, timeout=None, deregister=None):
        """
        Attempt to establish a tcp connection to the specified *host* and
        *port* at a specified *interval* with optional *timeout* and optional
        *deregister* after which a failing service will be automatically
        deregistered.
        """
        ret = {
            'tcp': '{host:s}:{port:d}'.format(host=host, port=port),
            'interval': interval
        }
        if timeout:
            ret['timeout'] = timeout
        if deregister:
            ret['DeregisterCriticalServiceAfter'] = deregister
        return ret

    @classmethod
    def ttl(klass, ttl):
        """
        Set check to be marked as critical after *ttl* (e.g. "10s") unless the
        check is periodically marked as passing.
        """
        return {'ttl': ttl}

    @classmethod
    def docker(klass, container_id, shell, script, interval, deregister=None):
        """
        Invoke *script* packaged within a running docker container with
        *container_id* at a specified *interval* on the configured
        *shell* using the Docker Exec API.  Optional *register* after which a
        failing service will be automatically deregistered.
        """
        ret = {
            'docker_container_id': container_id,
            'shell': shell,
            'script': script,
            'interval': interval
        }
        if deregister:
            ret['DeregisterCriticalServiceAfter'] = deregister
        return ret

    @classmethod
    def _compat(
            self,
            script=None,
            interval=None,
            ttl=None,
            http=None,
            timeout=None,
            deregister=None):

        if not script and not http and not ttl:
            return {}

        self.logger.warning(
            'DEPRECATED: use nomad.Check.script/http/ttl to specify check')

        ret = {'check': {}}

        if script:
            assert interval and not (ttl or http)
            ret['check'] = {'script': script, 'interval': interval}
        if ttl:
            assert not (interval or script or http)
            ret['check'] = {'ttl': ttl}
        if http:
            assert interval and not (script or ttl)
            ret['check'] = {'http': http, 'interval': interval}
        if timeout:
            assert http
            ret['check']['timeout'] = timeout

        if deregister:
            ret['check']['DeregisterCriticalServiceAfter'] = deregister

        return ret


Response = collections.namedtuple('Response', ['code', 'headers', 'body'])


#
# Conveniences to create consistent callback handlers for endpoints

class CB(object):
    @classmethod
    def __status(klass, response, allow_404=True):
        # status checking
        if response.code >= 500 and response.code < 600:
            raise NomadException("%d %s" % (response.code, response.body))
        if response.code == 400:
            raise BadRequest('%d %s' % (response.code, response.body))
        if response.code == 401:
            raise ACLDisabled(response.body)
        if response.code == 403:
            raise ACLPermissionDenied(response.body)
        if response.code == 404 and not allow_404:
            raise NotFound(response.body)

    @classmethod
    def bool(klass):
        # returns True on successful response
        def cb(response):
            CB.__status(response)
            return response.code == 200
        return cb

    @classmethod
    def json(
            klass,
            map=None,
            allow_404=True,
            one=False,
            decode=False,
            is_id=False,
            index=False):
        """
        *map* is a function to apply to the final result.

        *allow_404* if set, None will be returned on 404, instead of raising
        NotFound.

        *index* if set, a tuple of index, data will be returned.

        *one* returns only the first item of the list of items. empty lists are
        coerced to None.

        *decode* if specified this key will be base64 decoded.

        *is_id* only the 'ID' field of the json object will be returned.
        """

        def cb(response):
            CB.__status(response, allow_404=allow_404)
            data = None
            if response.code in [200]:
                data = json.loads(response.body)

                if decode:
                    for item in data:
                        if item.get(decode) is not None:
                            item[decode] = base64.b64decode(item[decode])
                if is_id:
                    data = data['ID']
                if one:
                    if data == []:
                        data = None
                    if data is not None:
                        data = data[0]
                if map:
                    data = map(data)
            if index:
                return response.headers['X-Nomad-Index'], data
            return data
        return cb

    @classmethod
    def raw(
            klass,
            map=None,
            allow_404=True,
            one=False,
            decode=False,
            is_id=False,
            index=False):
        """
        *map* is a function to apply to the final result.

        *allow_404* if set, None will be returned on 404, instead of raising
        NotFound.

        *index* if set, a tuple of index, data will be returned.

        *one* returns only the first item of the list of items. empty lists are
        coerced to None.

        *decode* if specified this key will be base64 decoded.

        *is_id* only the 'ID' field of the json object will be returned.
        """

        def cb(response):
            CB.__status(response, allow_404=allow_404)
            data = None
            if response.code in [200]:
                data = response.body
            if index:
                return response.headers['X-Nomad-Index'], data
            return data
        return cb


class HTTPClient(six.with_metaclass(abc.ABCMeta, object)):

    logger = getLogger("nomad_alt.HTTPClient")

    def __init__(self, host=None, port=None, scheme='http',
                 verify=True, cert=None, token=None, key=None, ca=None):
        self.host = host
        self.port = port
        self.scheme = scheme
        self.verify = verify
        self.base_uri = '%s://%s:%s' % (self.scheme, self.host, self.port)
        self.cert = cert
        self.key = key
        self.token = token
        self.ca = ca

        # self.logger.warn("verify: %s", verify)


    def uri(self, path, params=None):
        uri = self.base_uri + urllib.parse.quote(path, safe='/:')
        if params:
            uri = '%s?%s' % (uri, urllib.parse.urlencode(params))
        return uri

    @abc.abstractmethod
    def get(self, callback, path, params=None):
        raise NotImplementedError

    @abc.abstractmethod
    def put(self, callback, path, params=None, data=''):
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, callback, path, params=None):
        raise NotImplementedError

    @abc.abstractmethod
    def post(self, callback, path, params=None, data=''):
        raise NotImplementedError

class Nomad(object):
    def __init__(
            self,
            host=None,
            port=None,
            token=None,
            scheme=None,
            ssl_verify=None,
            ssl_cert=None,
            ssl_key=None,
            ssl_ca=None
    ):
        """

        All parameters are optional.

        The order of precedence is: params, environment variables, then defaults

        :param host: The address of the Nomad server (default 127.0.0.1)
        :param port: The port for the Nomad server (default 4646)
        :param scheme: The scheme using to communicate with the Nomad host (default to http)
        :param ssl_verify: Whether to verify the SSL certificate for HTTPS requests (default to False)

        :param token: ACL token. If supplied it will be used by
        default for all requests made with this client session. It's still
        possible to override this token by passing a token explicitly for a
        request.

        :param ssl_cert: Client side certificates for HTTPS requests
        :param ssl_key: Unencrypted PEM encoded private key matching the client certificate
        :param ssl_ca: path to a PEM encoded CA cert file to use to verify the Nomad server SSL certificate
        """

        # TODO: Status

        # The address of the Nomad server, including scheme, host, and port
        for nomad_host in [host, os.getenv('NOMAD_ADDR'), '127.0.0.1']:
            if nomad_host is not None:
                url_details = urlparse(nomad_host)
                address = "%s%s" % (url_details.netloc, url_details.path)
                addr_list = address.split(':')
                host = addr_list[0]
                if port is None and len(addr_list) > 1:
                    port = int(addr_list[1])
                if scheme is None and url_details.scheme != "":
                    scheme = url_details.scheme
                break
        port = port if port is not None else 4646
        scheme = scheme if scheme else 'http'

        # Verify TLS certificate
        ssl_verify = ssl_verify if ssl_verify is not None else not os.getenv('NOMAD_SKIP_VERIFY', 'true').lower() in ['true', 'on']

        # PEM encoded client certificate for TLS authentication to the Nomad server (Must also specify key)
        ssl_cert = ssl_cert if ssl_cert is not None else os.getenv('NOMAD_CLIENT_CERT')

        # unencrypted PEM encoded private key matching the client certificate
        ssl_key = ssl_key if ssl_key is not None else os.getenv('NOMAD_CLIENT_KEY')

        # Path to a PEM encoded CA cert file to use to verify the Nomad server SSL certificate
        ssl_ca = ssl_ca if ssl_ca is not None else os.getenv('NOMAD_CACERT')

        # The SecretID of an ACL token to use to authenticate API requests with
        self.token = token if token is not None else os.getenv('NOMAD_TOKEN')

        self.http = self.connect(host, port, scheme, ssl_verify, ssl_cert, self.token, ssl_key, ssl_ca)

        from nomad_alt.api.acl import Tokens as ACL_Tokens, Policies as ACL_Policies
        from nomad_alt.api.agent import Agent
        from nomad_alt.api.allocations import Allocations
        from nomad_alt.api.client import Client
        from nomad_alt.api.deployments import Deployments
        from nomad_alt.api.evaluations import Evaluations
        from nomad_alt.api.jobs import Jobs
        from nomad_alt.api.nodes import Nodes
        from nomad_alt.api.metrics import Metrics
        from nomad_alt.api.status import Status

        self.acl_policies = ACL_Policies(self)
        self.acl_tokens = ACL_Tokens(self)
        self.agent = Agent(self)
        self.allocations = Allocations(self)
        self.client = Client(self)
        self.deployments = Deployments(self)
        # self.deployments = Deployments(self)
        self.evaluations = Evaluations(self)
        self.jobs = Jobs(self)
        # self.namespaces = Namespaces(self)
        self.nodes = Nodes(self)
        self.metrics = Metrics(self)
        # self.operator = Operator(self)
        # self.quotas = Quotas(self)
        # self.regions = Regions(self)
        # self.search = Search(self)
        # self.sentinel_policies = Sentinel_Policies(self)
        self.status = Status(self)
        # self.validate = Validate(self)

    def connect(self, host, port, scheme, verify, cert, token, key, ca):
        pass
