Here are the final pieces for your project. Having a `Makefile` will make running these scripts a breeze, and a well-written `README.md` ensures that if anyone else on your team needs to use this tool, they have all the context they need.

### 1. The `Makefile`

Create a file named exactly `Makefile` (no extension) in the same directory as your scripts.

> [!IMPORTANT]
> Makefiles are notoriously strict about indentation. **You must use a real TAB character**, not spaces, for the indented lines below the commands.

```makefile
.PHONY: install audit rotate clean

# Installs the required Python packages
install:
	pip install -r requirements.txt

# Runs the main audit script to generate the Excel report
audit:
	python3 rancher-audit.py

# Runs the token rotation script and creates a backup of the config
rotate:
	python3 rotate-rancher-tokens.py

# Cleans up the directory by removing the spreadsheet and config backups
clean:
	rm -f *.xlsx *.bak
	@echo "Cleaned up Excel reports and config backups."

```

---

### 2. The `README.md`

Create a file named `README.md` and paste the following documentation into it.

```markdown
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

```

3. **Install Dependencies** using the included Makefile:
```bash
make install

```



## Configuration (`config.yaml`)

You must create a `config.yaml` file in the root directory. This file dictates which Rancher servers the script queries.

**Format:**

```yaml
rancher_instances:

  - name: "Production-Rancher"
    url: "[https://rancher.example.com](https://rancher.example.com)"
    token: "token-abcde:1234567890abcdefghijklmnopqrstuvwxyz"
    comment: "Main production management plane"

  - name: "Dev-Rancher"
    url: "[https://rancher-dev.example.com](https://rancher-dev.example.com)"
    token: "token-vwxyz:zyxwvutsrqponmlkjihgfedcba0987654321"
    comment: "Sandbox for testing k8s upgrades"

```

### How to get a Rancher API Token:

1. Log in to your Rancher UI.
2. Click your User Avatar (top right) -> **Account & API Keys**.
3. Click **Create API Key**.
4. Set Scope to **"No Scope"** (to ensure visibility across all clusters).
5. Copy the generated **Bearer Token** string (it will look like `token-xxxxx:xxxxxxxxxxxxxxxx`) and paste it into the YAML file.

> **Security Note:** Add `config.yaml` to your `.gitignore` file to prevent accidentally committing your credentials to version control.

## Usage

You can use standard Python commands or the included `Makefile` shortcuts.

### 1. Run the Audit Report

Queries all instances and generates a formatted `rancher_inventory.xlsx` file in the current directory.

```bash
make audit

```

### 2. Rotate API Tokens

Creates a new 30-day API token for every instance in your `config.yaml`, verifies the new token works, revokes the old token, and safely overwrites your `config.yaml` with the new credentials. A timestamped `.bak` file is created automatically.

```bash
make rotate

```

### 3. Cleanup

Removes all generated `.xlsx` spreadsheets and `.bak` config backups to tidy up the directory.

```bash
make clean

```

```

### Final Directory Structure
Your project folder should now look exactly like this:
* `rancher-audit.py` (The main script)
* `rotate-rancher-tokens.py` (The rotation script)
* `requirements.txt` (Your dependencies)
* `config.yaml` (Your credentials)
* `Makefile` (Your command shortcuts)
* `README.md` (Your documentation)

**Would you like me to guide you on how to set up a Git repository for this folder and push it to a remote server (making sure the `config.yaml` is safely ignored)?**

```
