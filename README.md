# Rancher Multi-Environment Audit Tool

A Python-based automation tool designed to interact with multiple SUSE Rancher management servers via the v3 API. It gathers deep inventory data on the management planes, standard downstream Kubernetes clusters (EKS, RKE, K3s, Custom), and Harvester HCI environments, exporting the data into a cleanly formatted, executive-ready Excel spreadsheet.

## Features
* **Multi-Instance Support**: Query multiple Rancher instances simultaneously.
* **Smart Provider Detection**: Accurately maps internal drivers to human-readable providers (AWS EKS, Harvester, Imported, Local, Virtual, Custom).
* **Deep Node Inspection**: Extracts AWS Regions, CPU Architectures (`amd64`/`arm64`), and OS Images directly from underlying node metadata.
* **Capacity Aggregation**: Calculates true allocatable CPU, Memory (in GiB), and Pod capacity.
* **Token Rotation**: Includes a standalone script to safely auto-rotate Rancher Bearer tokens without requiring manual UI intervention.

## Prerequisites
* Python 3.8+
* Valid Rancher API Bearer Tokens ("No Scope" required for full visibility)

## Setup & Installation

1. **Clone/Download the repository** to your local machine.
2. **(Optional but recommended)** Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
