from json import dumps
from nomad_alt.base import CB


class Policies(object):
    """
The /acl/policies and /acl/policy/ endpoints are used to manage ACL policies.
For more details about ACLs, please see the ACL Guide.
"""

    def __init__(self, agent):
        self.agent = agent

    def list(self):
        """
        This endpoint lists all ACL policies. This lists the policies that have been replicated to the region, and may lag behind the authoritative region.

        :return: json
        """
        return self.agent.http.get(
            CB.json(index=False, allow_404=False),
            '/v1/acl/policies')

    def set(self, policy_name, rules, description=None):
        """
This endpoint creates or updates an ACL Policy. This request is always forwarded to the authoritative region.

        :param: name (string: <required>) - Specifies the name of the policy. Creates the policy if the name does not exist, otherwise updates the existing policy.
        :param: rules (string: <required>) - Specifies the Policy rules in HCL or JSON format.
        :param: Description (string: <optional>) - Specifies a human readable description.

        :return: json
        """
        data = {'Name': policy_name, 'Rules': rules}
        if description is not None:
            data['Description'] = description
        data = dumps(data)
        return self.agent.http.post(
            CB.bool(), '/v1/acl/policy/%s' % policy_name, data=data)

    def read(self, policy_name):
        """
This endpoint reads an ACL policy with the given name. This queries the policy that have been replicated to the region, and may lag behind the authoritative region.

        :param: policy_name (string: <required>) - Specifies the policy name to read.

        :return: json
        """
        return self.agent.http.get(
            CB.json(index=False, allow_404=False),
            '/v1/acl/policy/%s' % policy_name)

    def delete(self, policy_name):
        """
This endpoint deletes the named ACL policy. This request is always forwarded to the authoritative region.

        :param: policy_name (string: <required>) - Specifies the policy name to delete.

        :return: boolean
        """
        return self.agent.http.delete(
            CB.bool(), '/v1/acl/policy/%s' % policy_name)

class Tokens(object):
    def __init__(self, agent):
        self.agent = agent

    def bootstrap(self):
        """
        This endpoint is used to bootstrap the ACL system and provide the initial management token. This request is always forwarded to the authoritative region. It can only be invoked once until a bootstrap reset is performed.

        :return: json
        """
        return self.agent.http.post(
            CB.json(index=False, allow_404=False),
            '/v1/acl/bootstrap')

    def list(self):
        """
        This endpoint lists all ACL tokens. This lists the local tokens and the global tokens which have been replicated to the region, and may lag behind the authoritative region.

        :return: json
        """
        return self.agent.http.get(
            CB.json(index=False, allow_404=False),
            '/v1/acl/tokens')

    def create(self, token_type, policies_array, name=None, make_global=False):
        """
        This endpoint creates an ACL Token. If the token is a global token, the request is forwarded to the authoritative region.

        :param: token_type - Specifies the type of token. Must be either client or management.
        :param: policies_array - Must be null or blank for management type tokens, otherwise must specify at least one policy for client type tokens.
        :param: name (optional) - Specifies the human readable name of the token.
        :param: make_global (optional - Defaults to False) - If true, indicates this token should be replicated globally to all regions. Otherwise, this token is created local to the target region.

        :return: json
        """
        data = {'Type': token_type, 'Policies': policies_array}
        if name is not None:
            data['Name'] = name
        data['Global'] = make_global
        data = dumps(data)
        print("Create Token: %s" % data)
        return self.agent.http.post(
            CB.json(index=False, allow_404=False),
            '/v1/acl/token', data=data)

    def update(self, accessor_id, token_type, policies_array, name=None):
        """
        This endpoint updates an existing ACL Token. If the token is a global token, the request is forwarded to the authoritative region. Note that a token cannot be switched from global to local or visa versa.

        :param: accessor_id (string: <required>) - Specifies the token (by accessor) that is being updated. Must match payload body and request path.
        :param: token_type (string: <required>) - Specifies the type of token. Must be either client or management.
        :param: policies_array (array<string>: <required>) - Must be null or blank for management type tokens, otherwise must specify at least one policy for client type tokens.
        :param: name (string: <optional>) - Specifies the human readable name of the token.

        :return: json
        """
        data = {'AccessorID': accessor_id, 'Type': token_type, 'Policies': policies_array}
        if name is not None:
            data['Name'] = name
        data = dumps(data)
        return self.agent.http.post(
            CB.json(index=False, allow_404=False),
            '/v1/acl/token/%s' % accessor_id, data=data)

    def read(self, accessor_id="self"):
        """
        This endpoint reads an ACL token with the given accessor. If the token is a global token which has been replicated to the region it may lag behind the authoritative region.

        :param: accessor_id (string: defaults to 'self') - Specifies the token (by accessor) that is being retrieved.

        :return: json
        """
        return self.agent.http.get(
            CB.json(index=False, allow_404=False),
            '/v1/acl/token/%s' % accessor_id)

    def delete(self, accessor_id):
        """
        This endpoint deletes the ACL token by accessor. This request is forwarded to the authoritative region for global tokens.

        :param: accessor_id (string: <required>) - Specifies the ACL token accessor ID.

        :return: json
        """
        return self.agent.http.delete(
            CB.bool(), '/v1/acl/token/%s' % accessor_id)
