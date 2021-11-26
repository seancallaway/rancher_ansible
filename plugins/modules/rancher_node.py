#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2020, Sean Callaway <seancallaway@gmail.com>
# MIT License (see LICENSE or https://opensource.org/licenses/MIT)
import json
import requests
from time import sleep
from ansible.module_utils.basic import AnsibleModule


def get_node(name, api_url, headers, validate_certs=True):
    """Returns a dict containing API results for the node if found.

    Returns None if not just one node is found
    """
    url = "{}/v3/nodes?name={}".format(api_url, name)
    node_search = requests.get(url, headers=headers, verify=validate_certs)
    if node_search.json()['pagination']['total'] > 1 or node_search.json()['pagination']['total'] == 0:
        return None
    return node_search.json()['data'][0]


def check_drain_status(name, api_url, headers, validate_certs=True):
    """Checks to see if a node has drained.

    Returns:
        1 if drained
        0 if draining
        -1 if drain failed
    """
    node = get_node(name, api_url, headers, validate_certs)
    if node['state'] == 'drained':
        return 1
    elif node['state'] == 'draining':
        return 0
    else:
        return -1


def rancher_node_drained(data):
    is_error = False
    has_changed = False
    meta = {}

    headers = {
        "Authorization": "Bearer {}".format(data['api_bearer_key'])
    }

    node = get_node(data['name'], data['rancher_url'], headers, data['validate_certs'])
    if not node:
        return True, False, {'error': 'Node name not found or multiple nodes found.'}
    if node['state'] == 'drained':
        meta = node
    else:
        drain_url = node['actions']['drain']
        drain_data = {
            "deleteLocalData": data['deleteLocalData'],
            "force": data['force'],
            "ignoreDaemonSets": data['ignoreDaemonSets'],
            "gracePeriod": data['gracePeriod'],
            "timeout": data['timeout'],
        }
        drain = requests.post(drain_url, data=json.dumps(drain_data),
                              headers=headers, verify=data['validate_certs'])
        meta = drain

        if drain.status_code == 200:
            drain_status = check_drain_status(node['name'], data['rancher_url'], headers, data['validate_certs'])
            interval = 5
            elapsed_time = 0
            while drain_status == 0 and elapsed_time < data['timeout']:
                sleep(interval)
                elapsed_time += interval
                drain_status = check_drain_status(node['name'], data['rancher_url'], headers, data['validate_certs'])
            if drain_status == 1:
                has_changed = True
                meta = {"status": "SUCCESS"}
            else:
                return True, True, {"status": "DRAIN FAILURE"}
        else:
            meta = {"status": drain.status_code, "response": drain.json()}

    return is_error, has_changed, meta


def rancher_node_cordoned(data):
    is_error = False
    has_changed = False
    meta = {}

    headers = {
        "Authorization": "Bearer {}".format(data['api_bearer_key'])
    }

    node = get_node(data['name'], data['rancher_url'], headers, data['validate_certs'])
    if not node:
        return True, False, {'error': 'Node name not found or multiple nodes found.'}
    if node['state'] == 'cordoned':
        meta = node
    else:
        cordon_url = node['actions']['cordon']
        cordon = requests.post(cordon_url, data=json.dumps({}),
                               headers=headers, verify=data['validate_certs'])
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

    node = get_node(data['name'], data['rancher_url'], headers, data['validate_certs'])
    if not node:
        return True, False, {'error': 'Node name not found or multiple nodes found.'}
    if node['state'] == 'active':
        meta = node
    else:
        uncordon_url = node['actions']['uncordon']
        uncordon = requests.post(uncordon_url, data=json.dumps({}),
                                 headers=headers, verify=data['validate_certs'])
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
        "api_bearer_key": {"required": True, "type": "str", "no_log": True},
        "force": {"default": False, "type": "bool"},
        "deleteLocalData": {"default": False, "type": "bool"},
        "ignoreDaemonSets": {"default": True, "type": "bool"},
        "timeout": {"default": 120, "type": "int"},
        "gracePeriod": {"default": -1, "type": "int"},
        "validate_certs": {"default": False, "type": "bool"},
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
