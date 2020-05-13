#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2020, Sean Callaway <seancallaway@gmail.com>
# MIT License (see LICENSE or https://opensource.org/licenses/MIT)
import json
import requests
from ansible.module_utils.basic import AnsibleModule


def get_node(name, api_url, headers):
    """Returns a dict containing API results for the node if found.

    Returns None if not just one node is found
    """
    url = "{}/v3/nodes?name={}".format(api_url, name)
    node_search = requests.get(url, headers=headers)
    if node_search.json()['pagination']['total'] > 1 or node_search.json()['pagination']['total'] == 0:
        return None
    return node_search.json()['data'][0]


def rancher_node_drained(data):
    is_error = False
    has_changed = False
    meta = {"drained": "not yet implemented"}
    return is_error, has_changed, meta


def rancher_node_cordoned(data):
    is_error = False
    has_changed = False
    meta = {}

    headers = {
        "Authorization": "Bearer {}".format(data['api_bearer_key'])
    }

    node = get_node(data['name'], data['rancher_url'], headers)
    if not node:
        return True, False, {'error': 'Node name not found or multiple nodes found.'}
    if node['state'] == 'cordoned':
        meta = node
    else:
        cordon_url = node['actions']['cordon']
        cordon = requests.post(cordon_url, data=json.dumps({}), headers=headers)
        meta = cordon

        if cordon.status_code == 200:
            has_changed = True
            meta = {"status": "SUCCESS"}
        else:
            meta = {"status": cordon.status_code, "response": cordon.json()}

    return is_error, has_changed, meta


def rancher_node_uncordoned(data):
    is_error = False
    has_changed = False
    meta = {}

    headers = {
        "Authorization": "Bearer {}".format(data['api_bearer_key'])
    }

    node = get_node(data['name'], data['rancher_url'], headers)
    if not node:
        return True, False, {'error': 'Node name not found or multiple nodes found.'}
    if node['state'] == 'active':
        meta = node
    else:
        uncordon_url = node['actions']['uncordon']
        uncordon = requests.post(uncordon_url, data=json.dumps({}), headers=headers)
        meta = uncordon

        if uncordon.status_code == 200:
            has_changed = True
            meta = {"status": "SUCCESS"}
        else:
            meta = {"status": uncordon.status_code, "response": uncordon.json()}

    return is_error, has_changed, meta


def main():
    fields = {
        "name": {"required": True, "type": "str"},
        "rancher_url": {"required": True, "type": "str"},
        "api_bearer_key": {"required": True, "type": "str"},
        "state": {
            "default": "uncordoned",
            "choices": ["drained", "cordoned", "uncordoned"],
            "type": "str",
        },
    }
    choice_map = {
        'drained': rancher_node_drained,
        'cordoned': rancher_node_cordoned,
        'uncordoned': rancher_node_uncordoned,
    }
    module = AnsibleModule(argument_spec=fields)
    is_error, has_changed, result = choice_map.get(module.params['state'])(module.params)
    if not is_error:
        module.exit_json(changed=has_changed, meta=result)
    else:
        module.fail_json(msg="Error adjusting node", meta=result)


if __name__ == '__main__':
    main()
