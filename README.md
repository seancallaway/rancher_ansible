# Rancher Modules
> Ansible Modules for Rancher

An Ansible Collection providing modules for interfacing with Rancher.

Contains the following modules:

- `rancher_cluster` for creating, deleting, and gathering information about custom clusters
- `rancher_node` for cordoning, draining, and uncordoning nodes

## Example Usage

### Importing The Collection

`ansible-galaxy collection install seancallaway.rancher`

### Using the Modules

#### rancher_cluster

```yaml
- hosts: localhost
  gather_facts: no
  tasks:
  - name: Create Cluster
    rancher_cluster:
      name: test-cluster
      description: Test Cluster Created with Ansible
      rancher_url: https://rancher.mydomain.com
      api_bearer_key: token-fg3ea:asdfimnoaqipnweron92u09jpqvijw490aqwekmowipcn
      network_plugin: canal
      state: present
    register: test_cluster
```

Note that the activation command (minus the `--worker`, `--etcd`, or `--controlplane` flags) is returned as 
`registration_token`.

The following shows a more complete example of the usage of the `rancher_cluster` module including all optional parameters:

```yaml
- hosts: localhost
  gather_facts: no
  tasks:
  - name: Create rancher cluster including optional parameters
    rancher_cluster:
      name: test-cluster2
      description: Another test cluster created via Ansible
      rancher_url: https://rancher.mydomain.com
      api_bearer_key: token-xyz:abcdefg0123456789
      network_plugin: calico
      agentImageOverride: my-org/my-image
      desiredAgentImage: my-org/my-image
      desiredAuthImage: my-org/my-image
      dockerRootDir: /var/lib/docker
      enableClusterAlerting: True
      enableClusterMonitoring: True
      ignore_docker_version: True
      validate_certs: True
      labels:
        mylabel: Value
        other_label: Value
      annotations:
        first_annotation: "Value"
        second_annotation: "Another value"
```

#### rancher_node

```yaml
- hosts: localhost
  gather_facts: no
  tasks:
  - name: Cordon Node
    rancher_node:
      name: worker01
      rancher_url: https://rancher.mydomain.com
      api_bearer_key: token-fg3ea:asdfimnoaqipnweron92u09jpqvijw490aqwekmowipcn
      state: cordoned
  - name: Drain Node
    rancher_node:
      name: worker03
      rancher_url: https://rancher.mydomain.com
      api_bearer_key: token-fg3ea:asdfimnoaqipnweron92u09jpqvijw490aqwekmowipcn
      force: true
      deleteLocalData: true
      state: drained
  - name: Uncordon Node
    rancher_node:
      name: worker01
      rancher_url: https://rancher.mydomain.com
      api_bearer_key: token-fg3ea:asdfimnoaqipnweron92u09jpqvijw490aqwekmowipcn
      state: uncordoned
```
