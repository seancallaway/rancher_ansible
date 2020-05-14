# Rancher Modules
> Ansible Modules for Rancher

None of these are ready for use. When they are, they'll be converted to a collection and placed in Galaxy.

## Example Usage

### rancher_cluster

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

### rancher_node

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
```

