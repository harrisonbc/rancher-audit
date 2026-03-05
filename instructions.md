You are totally right—nesting those Markdown code blocks inside a bash command can definitely cause parsers to trip up and break the formatting!

Here is the pure, complete Markdown for your `instructions.md` file. You can copy this block directly and paste it into your editor:

```markdown
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

```

## 2. Running the Audit

Execute the script using the terminal. If you are using a Python virtual environment, ensure it is activated before running.

```bash
make audit

```

*(Alternatively, you can run `python3 rancher-audit.py` directly).*

### Terminal Output

As the script runs, it evaluates the support status of every cluster in real-time. You will see terminal output utilizing standard traffic light emojis:

* 🟩 **[GREEN]**: The version is fully supported.
* 🟨 **[YELLOW]**: The version has passed its End of Maintenance (EOM) date or is within 60 days of End of Life. Plan upgrades immediately.
* 🟥 **[RED]**: The version is End of Life (EOL). It is unsupported and potentially insecure.

## 3. Interpreting the Outputs

The script automatically generates two artifacts in your local directory:

### Artifact A: `rancher_inventory.xlsx`

A highly formatted Excel spreadsheet broken into three tables:

1. **Management Server Summary:** Details the control planes.
2. **Harvester Clusters:** Details your bare-metal virtualization layers.
3. **Managed Downstream Clusters:** Details your standard Kubernetes workloads.

**Visual Indicators:**

* **Version Cells:** Dynamically turn Green, Yellow, or Red based on the lifecycle API.
* **Region Cells (Downstream):** If a downstream cluster is deployed in a different region than its parent Rancher server, the Region cell will turn **Red** to alert you to potential latency or cross-region egress costs.

### Artifact B: `rancher_architecture.md`

A markdown file containing a top-down `Mermaid.js` topology map of your entire infrastructure.

**How to View the Diagram:**
Because this diagram uses rich HTML formatting and Unicode indicator blocks (🟩 🟨 🟥) for maximum readability, it requires a standard Markdown renderer.

* **Method 1 (Quickest):** Copy the code block and paste it into the official [Mermaid Live Editor](https://mermaid.live).
* **Method 2 (Native):** Commit the `.md` file to your Git repository (GitHub/GitLab) and view it directly in your web browser.
* **Method 3 (Local):** Use a Markdown viewer like Obsidian, Notion, or the VS Code "Markdown Preview Mermaid Support" extension.
*(Note: Excalidraw's Mermaid importer strips HTML tags and is not recommended for this specific diagram format).*

```

Would you like me to output the pure Markdown for the `README.md` file as well, just to make sure that one formats perfectly for you too?

```
