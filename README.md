# Rancher Multi-Cluster Audit Tool

An automated, Python-based auditing script designed to query multiple Rancher management servers, extract downstream cluster and Harvester hypervisor inventory, and generate compliance-ready Excel reports and architecture diagrams.

## 🚀 Key Features

* **Multi-Instance Support:** Query multiple Rancher Management planes simultaneously using Bearer tokens.
* **Dynamic Lifecycle Tracking:** Integrates with the `endoflife.date` API to dynamically evaluate Kubernetes and Rancher versions, automatically flagging them as Supported (Green), Warning/End of Maintenance (Yellow), or End of Life (Red).
* **Harvester Lifecycle Support:** Includes a built-in lifecycle matrix to track Harvester bare-metal hypervisor support windows.
* **Cross-Region Compliance:** Automatically detects and flags downstream clusters that are deployed in a different AWS region than their managing Rancher control plane.
* **Color-Coded Excel Reporting:** Generates a highly formatted `rancher_inventory.xlsx` spreadsheet with traffic-light styling for immediate visual identification of aging infrastructure.
* **Automated Architecture Diagrams:** Generates a rich-HTML Mermaid diagram (`rancher_architecture.md`) mapping your entire infrastructure topology, complete with version badges, health status blocks (🟩 🟨 🟥), and region tracking.

## 📋 Prerequisites

* Python 3.8+
* A generic `config.yaml` file containing your Rancher API tokens.

**Required Python Libraries:**
`requests`, `pandas`, `urllib3`, `pyyaml`, `xlsxwriter`
*(Install via `pip install -r requirements.txt` or `make install` if using the provided Makefile).*

## 🛠️ Usage

1. Clone the repository.
2. Ensure your `config.yaml` is populated with your environment details.
3. Run the audit via Make:
   \`make audit\`
4. Review the real-time terminal output, then open `rancher_inventory.xlsx` and `rancher_architecture.md`.

## Status
Ready for production.
