# Operational Instructions: Rancher Audit Tool

This guide explains how to configure, run, and interpret the outputs of the Rancher Audit script.

## 1. Configuration Setup
The script relies on a local `config.yaml` file to authenticate with your Rancher instances. This file **must not** be committed to version control to protect your API tokens. 

Create a file named `config.yaml` in the root directory formatted like this:

```yaml
rancher_instances:
  - name: "AWS Rancher"
    url: "[https://rancher.yourdomain.com](https://rancher.yourdomain.com)"
    token: "token-abcde:1234567890abcdef"
    comment: "Primary Production Management Plane"
  
  - name: "Rancher Prime"
    url: "[https://rancher-prime.yourdomain.com](https://rancher-prime.yourdomain.com)"
    token: "token-fghij:0987654321fedcba"
    comment: "Internal Tooling and Test Clusters"
