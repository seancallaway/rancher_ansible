#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2020, Sean Callaway <seancallaway@gmail.com>
# MIT License (see LICENSE or https://opensource.org/licenses/MIT)
import json
import requests
from ansible.module_utils.basic import AnsibleModule


def rancher_cluster_present(data):
    """Run when state: present"""

    api_key = data['api_bearer_key']
    api_url = data['rancher_url']

    ignore_docker_version = data['ignore_docker_version']
    network_plugin = data['network_plugin']

    del data['state']
    del data['api_bearer_key']
    del data['rancher_url']
    del data['ignore_docker_version']
    del data['network_plugin']

    data['type'] = 'cluster'
    data['rancherKubernetesEngineConfig'] = {
        "addonJobTimeout": 30,
        "ignoreDockerVersion": ignore_docker_version,
        "sshAgentAuth": False,
        "type": "rancherKubernetesEngineConfig",
        "authentication": {
            "type": "authnConfig",
            "strategy": "x509"
        },
        "network": {
            "type": "networkConfig",
            "plugin": network_plugin
        },
        "ingress": {
            "type": "ingressConfig",
            "provider": "nginx"
        },
        "monitoring": {
            "type": "monitoringConfig",
            "provider": "metrics-server"
        },
        "services": {
            "type": "rkeConfigServices",
            "kubeApi": {
                "podSecurityPolicy": False,
                "type": "kubeAPIService"
            },
            "etcd": {
                "snapshot": False,
                "type": "etcdService",
                "extraArgs": {
                    "heartbeat-interval": 500,
                    "election-timeout": 5000
                }
            }
        }
    }

    headers = {
        "Authorization": "Bearer {}".format(api_key)
    }
    url = "{}{}".format(api_url, '/v3/clusters')
    result = requests.post(url, json.dumps(data), headers=headers)

    if result.status_code == 201:
        token_url = "{}{}".format(api_url, '/v3/clusterregistrationtoken')
        token_data = {
            "type": "clusterRegistrationToken",
            "clusterId": result.json()['id'],
        }
        token_request = requests.post(token_url, json.dumps(token_data), headers=headers)
        meta = result.json()
        meta['registration_token'] = token_request.json()['nodeCommand']
        return False, True, meta
    elif result.status_code == 422:
        # This is returned when the cluster already exists, too.
        return False, False, result.json()

    # default: something went wrong
    meta = {"status": result.status_code, "response": result.json()}
    return True, False, meta


def rancher_cluster_absent(data):
    """Run when state: absent"""

    # Find cluster by name
    headers = {
        "Authorization": "Bearer {}".format(data['api_bearer_key'])
    }
    url = "{}{}?name={}".format(data['rancher_url'], '/v3/clusters', data['name'])
    search_result = requests.get(url, headers=headers)
    if search_result.json()['pagination']['total'] > 1:
        return True, False, {"error": "Multiple clusters found using the provided name"}
    elif search_result.json()['pagination']['total'] == 0:
        return False, False, {"msg": "No clusters found using the provided name"}

    delete_link = search_result.json()['data'][0]['links']['remove']
    delete_result = requests.delete(delete_link, headers=headers)

    if delete_result.status_code == 200:
        return False, True, delete_result.json()
    elif delete_result.status_code == 422:
        return False, False, delete_result.json()

    # default: something went wrong
    meta = {"status": delete_result.status_code, "response": delete_result.json()}
    return True, False, meta


def main():

    fields = {
        "name": {"required": True, "type": "str"},
        "rancher_url": {"required": True, "type": "str"},
        "api_bearer_key": {"required": True, "type": "str"},
        "agentImageOverride": {"required": False, "type": "str"},
        "description": {"required": False, "type": "str"},
        "desiredAgentImage": {"required": False, "type": "str"},
        "desiredAuthImage": {"required": False, "type": "str"},
        "dockerRootDir": {"default": "/var/lib/docker", "type": "str"},
        "enableClusterAlerting": {"default": False, "type": "bool"},
        "enableClusterMonitoring": {"default": False, "type": "bool"},
        "ignore_docker_version": {"default": False, "type": "bool"},
        "network_plugin": {
            "default": "canal",
            "choices": ["canal", "calico", "flannel"],
            "type": "str",
        },
        "state": {
            "default": "present",
            "choices": ["present", "absent"],
            "type": "str",
        },
    }

    choice_map = {
        "present": rancher_cluster_present,
        "absent": rancher_cluster_absent,
    }

    module = AnsibleModule(argument_spec=fields)
    is_error, has_changed, result = choice_map.get(module.params['state'])(module.params)

    if not is_error:
        module.exit_json(changed=has_changed, meta=result)
    else:
        module.fail_json(msg="Something went wrong.", meta=result)


if __name__ == '__main__':
    main()
