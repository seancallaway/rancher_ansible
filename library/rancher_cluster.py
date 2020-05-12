#!/usr/bin/python
from ansible.module_utils.basic import *


def rancher_cluster_present(data):
    """Run when state: present"""
    has_changed = False
    meta = {"present": "not yet implemented"}
    return has_changed, meta


def rancher_cluster_absent(data):
    """Run when state: absent"""
    has_changed = False
    meta = {"absent": "not yet implemented"}
    return has_changed, meta


def main():

    fields = {
        "name": {"required": True, "type": "str"},
        "agentImageOverride": {"required": False, "type": "str"},
        "description": {"required": False, "type": "str"},
        "desiredAgentImage": {"required": False, "type": "str"},
        "desiredAuthImage": {"required": False, "type": "str"},
        "dockerRootDir": {"default": "/var/lib/docker", "type": "str"},
        "enableClusterAlerting": {"default": False, "type": "bool"},
        "enableClusterMonitoring": {"default": False, "type": "bool"},
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
    has_changed, result = choice_map.get(module.params['state'])(module.params)
    module.exit_json(changed=has_changed, meta=result)


if __name__ == '__main__':
    main()
