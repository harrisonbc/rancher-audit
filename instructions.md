**Install Dependencies** using the included Makefile:
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
