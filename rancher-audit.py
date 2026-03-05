import requests
import pandas as pd
import urllib3
import yaml
import os
import re
from datetime import datetime, timedelta

# Disabling SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Global caches for the lifecycle APIs
_K8S_LIFECYCLES = None
_RANCHER_LIFECYCLES = None

# Hardcoded Harvester Lifecycles (Since no public API exists for Harvester yet)
HARVESTER_LIFECYCLES = {
    "1.7": {"eom": "2026-08-09", "eol": "2027-08-09"},
    "1.6": {"eom": "2026-04-16", "eol": "2027-04-16"},
    "1.5": {"eom": "2025-12-30", "eol": "2026-12-30"},
    "1.4": {"eom": "2024-11-27", "eol": "2025-11-27"},
    "1.3": {"eom": "2024-06-13", "eol": "2025-06-13"},
    "1.2": {"eom": "2024-07-08", "eol": "2024-09-08"} 
}

def load_config(filepath="config.yaml"):
    if not os.path.exists(filepath):
        print(f"Error: Configuration file '{filepath}' not found.")
        return None
    try:
        with open(filepath, 'r') as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as exc:
        print(f"Error parsing YAML file: {exc}")
        return None

def parse_cpu(cpu_val):
    if not cpu_val: return "0"
    cpu_str = str(cpu_val)
    if cpu_str.endswith('m'):
        return str(round(int(cpu_str[:-1]) / 1000, 2))
    return cpu_str

def parse_memory(mem_val):
    if not mem_val: return "0 GiB"
    mem_str = str(mem_val)
    try:
        if mem_str.endswith('Ki'):
            return f"{round(int(mem_str[:-2]) / (1024**2), 2)} GiB"
        elif mem_str.endswith('Mi'):
            return f"{round(int(mem_str[:-2]) / 1024, 2)} GiB"
        elif mem_str.endswith('Gi'):
            return f"{mem_str[:-2]} GiB"
        elif mem_str.isdigit(): 
            return f"{round(int(mem_str) / (1024**3), 2)} GiB"
    except Exception:
        pass
    return mem_str

# ==========================================
# LIFECYCLE DATA FETCHERS & EVALUATORS
# ==========================================

def fetch_k8s_lifecycles():
    global _K8S_LIFECYCLES
    if _K8S_LIFECYCLES is not None:
        return _K8S_LIFECYCLES
    try:
        print("🌐 Fetching dynamic Kubernetes lifecycle data from endoflife.date...")
        resp = requests.get("https://endoflife.date/api/kubernetes.json", timeout=10)
        resp.raise_for_status()
        _K8S_LIFECYCLES = {item['cycle']: item['eol'] for item in resp.json()}
    except Exception as e:
        print(f"⚠️ Warning: Could not fetch K8s lifecycle data: {e}")
        _K8S_LIFECYCLES = {} 
    return _K8S_LIFECYCLES

def fetch_rancher_lifecycles():
    global _RANCHER_LIFECYCLES
    if _RANCHER_LIFECYCLES is not None:
        return _RANCHER_LIFECYCLES
    try:
        print("🌐 Fetching dynamic Rancher lifecycle data from endoflife.date...")
        resp = requests.get("https://endoflife.date/api/rancher.json", timeout=10)
        resp.raise_for_status()
        _RANCHER_LIFECYCLES = {}
        for item in resp.json():
            # endoflife.date provides 'support' (EOM) and 'eol' for Rancher
            eol = item.get('eol', '2000-01-01')
            eom = item.get('support')
            if not isinstance(eom, str):
                # Fallback to a 60-day warning window if EOM is missing
                eol_date = datetime.strptime(eol, "%Y-%m-%d").date()
                eom = (eol_date - timedelta(days=60)).strftime("%Y-%m-%d")
            _RANCHER_LIFECYCLES[item['cycle']] = {"eol": eol, "eom": eom}
    except Exception as e:
        print(f"⚠️ Warning: Could not fetch Rancher lifecycle data: {e}")
        _RANCHER_LIFECYCLES = {} 
    return _RANCHER_LIFECYCLES

def get_k8s_version_status(version_str, cluster_name="Unknown"):
    if not version_str or version_str in ["Unknown", "N/A"]: return "Unknown"
    match = re.search(r'v?(1\.\d+)', str(version_str))
    if not match: return "Unknown"
    minor_version = match.group(1)
    lifecycles = fetch_k8s_lifecycles()
    
    if not lifecycles or minor_version not in lifecycles:
        try:
            minor_num = int(minor_version.split('.')[1])
            if minor_num < 28: 
                print(f"    -> 🟥 [RED] K8s Cluster {cluster_name} (Version {version_str} is extremely old)")
                return "Red" 
            elif minor_num >= 34: 
                print(f"    -> 🟩 [GREEN] K8s Cluster {cluster_name} (Version {version_str} is brand new)")
                return "Green" 
        except Exception: pass
        return "Unknown"
        
    today = datetime.now().date()
    eol_date = datetime.strptime(lifecycles[minor_version], "%Y-%m-%d").date()
    warning_date = eol_date - timedelta(days=60)
    
    if today >= eol_date:
        print(f"    -> 🟥 [RED] K8s Cluster {cluster_name} (Version {version_str} passed EOL on {eol_date})")
        return "Red"
    elif today >= warning_date:
        print(f"    -> 🟨 [YELLOW] K8s Cluster {cluster_name} (Version {version_str} entered warning window on {warning_date})")
        return "Yellow"
    else:
        print(f"    -> 🟩 [GREEN] K8s Cluster {cluster_name} (Version {version_str} is supported)")
        return "Green"

def get_rancher_version_status(version_str, server_name="Unknown"):
    if not version_str or version_str in ["Unknown", "N/A"]: return "Unknown"
    match = re.search(r'v?(2\.\d+)', str(version_str))
    if not match: return "Unknown"
    minor_version = match.group(1)
    lifecycles = fetch_rancher_lifecycles()
    
    if not lifecycles or minor_version not in lifecycles:
        try:
            minor_num = int(minor_version.split('.')[1])
            if minor_num < 8: 
                print(f"    -> 🟥 [RED] Rancher Server {server_name} (Version {version_str} is extremely old)")
                return "Red" 
            elif minor_num >= 12: 
                print(f"    -> 🟩 [GREEN] Rancher Server {server_name} (Version {version_str} is brand new)")
                return "Green" 
        except Exception: pass
        return "Unknown"
        
    today = datetime.now().date()
    eol_date = datetime.strptime(lifecycles[minor_version]["eol"], "%Y-%m-%d").date()
    eom_date = datetime.strptime(lifecycles[minor_version]["eom"], "%Y-%m-%d").date()
    
    if today >= eol_date:
        print(f"    -> 🟥 [RED] Rancher Server {server_name} (Version {version_str} passed EOL on {eol_date})")
        return "Red"
    elif today >= eom_date:
        print(f"    -> 🟨 [YELLOW] Rancher Server {server_name} (Version {version_str} passed EOM on {eom_date})")
        return "Yellow"
    else:
        print(f"    -> 🟩 [GREEN] Rancher Server {server_name} (Version {version_str} is supported)")
        return "Green"

def get_harvester_version_status(version_str, cluster_name="Unknown"):
    if not version_str or version_str in ["Unknown", "N/A"]: return "Unknown"
    match = re.search(r'v?(1\.\d+)', str(version_str))
    if not match: return "Unknown"
    minor_version = match.group(1)
    
    if minor_version not in HARVESTER_LIFECYCLES:
        try:
            minor_num = int(minor_version.split('.')[1])
            if minor_num < 4: 
                print(f"    -> 🟥 [RED] Harvester {cluster_name} (Version {version_str} is extremely old)")
                return "Red"
            elif minor_num >= 8:
                print(f"    -> 🟩 [GREEN] Harvester {cluster_name} (Version {version_str} is brand new)")
                return "Green" 
        except Exception: pass
        return "Unknown"
        
    today = datetime.now().date()
    eol_date = datetime.strptime(HARVESTER_LIFECYCLES[minor_version]["eol"], "%Y-%m-%d").date()
    eom_date = datetime.strptime(HARVESTER_LIFECYCLES[minor_version]["eom"], "%Y-%m-%d").date()
    
    if today >= eol_date:
        print(f"    -> 🟥 [RED] Harvester {cluster_name} (Version {version_str} passed EOL on {eol_date})")
        return "Red"
    elif today >= eom_date:
        print(f"    -> 🟨 [YELLOW] Harvester {cluster_name} (Version {version_str} passed EOM on {eom_date})")
        return "Yellow"
    else:
        print(f"    -> 🟩 [GREEN] Harvester {cluster_name} (Version {version_str} is supported)")
        return "Green"

# ==========================================
# STANDARD AUDIT FUNCTIONS
# ==========================================

def get_server_summary(instance):
    headers = {"Authorization": f"Bearer {instance['token']}"}
    base_url = instance['url'].rstrip('/')
    clean_url = instance['url'].replace("https://", "").replace("http://", "").rstrip('/')
    
    summary = {
        "Name": instance['name'],
        "URL": clean_url,
        "Rancher Version": "Unknown",
        "Local K8s Version": "Unknown",
        "AWS Region": "N/A",
        "Backup Operator": "Not Found",
        "Config Comment": instance.get('comment', "")
    }

    try:
        v_resp = requests.get(f"{base_url}/v3/settings/server-version", headers=headers, verify=False, timeout=10)
        if v_resp.status_code == 200:
            summary["Rancher Version"] = v_resp.json().get('value', 'Unknown')

        c_resp = requests.get(f"{base_url}/v3/clusters/local", headers=headers, verify=False, timeout=10)
        if c_resp.status_code == 200:
            c_data = c_resp.json()
            summary["Local K8s Version"] = c_data.get('version', {}).get('gitVersion', 'N/A')
            
            region = ""
            for key in ['amazonElasticContainerServiceConfig', 'eksConfig']:
                if c_data.get(key):
                    region = c_data[key].get('region', '')
            
            if not region:
                node_meta = get_node_metadata(base_url, 'local', headers)
                region = node_meta.get("region", "")
                
            summary["AWS Region"] = region if region else "N/A"

        crd_resp = requests.get(f"{base_url}/v1/apiextensions.k8s.io.customresourcedefinitions/backups.resources.cattle.io", headers=headers, verify=False, timeout=10)
        if crd_resp.status_code == 200:
            summary["Backup Operator"] = "Installed"

    except Exception as e:
        print(f"⚠️ Error summarising {instance['name']}: {e}")
    
    return summary

def get_node_metadata(base_url, cluster_id, headers):
    metadata = {"region": "", "arch": "Unknown"}
    try:
        node_url = f"{base_url}/v3/clusters/{cluster_id}/nodes?limit=1"
        resp = requests.get(node_url, headers=headers, verify=False, timeout=10)
        
        if resp.status_code == 200:
            nodes = resp.json().get('data', [])
            if nodes:
                node = nodes[0]
                labels = node.get('labels', {})
                if not labels:
                    labels = node.get('info', {}).get('kubernetes', {}).get('labels', {})
                
                metadata["region"] = (
                    labels.get('topology.kubernetes.io/region') or 
                    labels.get('failure-domain.beta.kubernetes.io/region') or 
                    ""
                )
                metadata["arch"] = (
                    labels.get('kubernetes.io/arch') or 
                    labels.get('beta.kubernetes.io/arch') or 
                    "Unknown"
                )
    except Exception:
        pass
    return metadata

def get_harvester_version(base_url, cluster_id, headers):
    try:
        url = f"{base_url}/k8s/clusters/{cluster_id}/apis/harvesterhci.io/v1beta1/settings/server-version"
        resp = requests.get(url, headers=headers, verify=False, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            return data.get('value') or data.get('default') or "Unknown"
    except Exception as e:
        pass
    return "Unknown"

def get_cluster_data(instances):
    downstream_clusters = []
    harvester_clusters = []
    
    for instance in instances:
        print(f"\n🚀 Scanning Rancher Instance: {instance['name']}...")
        headers = {"Authorization": f"Bearer {instance['token']}"}
        base_url = instance['url'].rstrip('/')
        api_url = f"{base_url}/v3/clusters"

        try:
            response = requests.get(api_url, headers=headers, verify=False, timeout=15)
            response.raise_for_status()
            for cluster in response.json().get('data', []):

                cluster_id = cluster.get('id', '')
                git_version = cluster.get('version', {}).get('gitVersion', 'N/A')
                raw_driver = cluster.get('driver', '').lower()
                raw_provider = cluster.get('provider', '').lower()

                if cluster_id == 'local':
                    provider_type = 'Local'
                elif 'import' in raw_driver or 'import' in raw_provider:
                    provider_type = 'Imported'
                elif 'harvester' in raw_driver or 'harvester' in raw_provider:
                    provider_type = 'Harvester'
                else:
                    cloud_identifiers = ['eks', 'gke', 'aks', 'amazonec2', 'vsphere', 'azure', 'digitalocean', 'linode', 'amazonelasticcontainerservice']
                    is_virtual = any(cloud_id in raw_driver for cloud_id in cloud_identifiers)
                    if not is_virtual:
                        for key in cluster.keys():
                            if key.lower().endswith('config') and any(cloud_id in key.lower() for cloud_id in cloud_identifiers):
                                is_virtual = True
                                break
                    provider_type = 'Virtual' if is_virtual else 'Custom'

                region = ""
                arch = "Unknown"
                for key in ['amazonElasticContainerServiceConfig', 'eksConfig']:
                    if cluster.get(key):
                        region = cluster[key].get('region', '')
                
                if cluster_id:
                    node_meta = get_node_metadata(base_url, cluster_id, headers)
                    arch = node_meta["arch"]
                    if not region:
                        region = node_meta["region"]

                if provider_type == 'Harvester':
                    hv_version = get_harvester_version(base_url, cluster_id, headers)
                    harvester_clusters.append({
                        "Cluster Name": cluster.get('name'),
                        "Harvester Version": hv_version,
                        "Kubernetes Version": git_version,
                        "CPU Arch": arch,
                        "Rancher Server": instance['name'],
                        "Comments": ""
                    })
                else:
                    if '+rke2' in git_version: k8s_dist = 'RKE2'
                    elif '+k3s' in git_version: k8s_dist = 'K3s'
                    elif '-eks' in git_version or raw_driver in ['amazonelasticcontainerservice', 'eks']: k8s_dist = 'AWS EKS'
                    elif 'rancherkubernetesengine' in raw_driver: k8s_dist = 'RKE1'
                    else: k8s_dist = 'Upstream/Other'

                    allocatable = cluster.get('allocatable', {})
                    cpu_cores = parse_cpu(allocatable.get('cpu', '0'))
                    memory_gib = parse_memory(allocatable.get('memory', '0'))
                    pods = allocatable.get('pods', '0')

                    downstream_clusters.append({
                        "Rancher Server": instance['name'],
                        "Cluster Name": cluster.get('name'),
                        "Provider Type": provider_type,
                        "K8s Distribution": k8s_dist,
                        "Full K8s Version": git_version,
                        "CPU Arch": arch,
                        "Region": region if region else "N/A",
                        "CPU (Cores)": cpu_cores,
                        "Memory": memory_gib,
                        "Total Pods": pods,
                        "Comments": ""
                    })

        except Exception as e:
            print(f"⚠️ Error fetching clusters from {instance['name']}: {e}")
            
    return downstream_clusters, harvester_clusters

def save_styled_excel(server_summaries, downstream_clusters, harvester_clusters, filename="rancher_inventory.xlsx"):
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')
    workbook = writer.book
    worksheet = workbook.add_worksheet("Rancher Inventory")

    title_fmt = workbook.add_format({'bold': True, 'font_size': 12, 'bg_color': '#D7E4BC', 'border': 1})
    harvester_title_fmt = workbook.add_format({'bold': True, 'font_size': 12, 'bg_color': '#FCE4D6', 'border': 1})
    header_fmt = workbook.add_format({'bold': True, 'font_color': 'white', 'bg_color': '#217346', 'border': 1})
    harvester_header_fmt = workbook.add_format({'bold': True, 'font_color': 'white', 'bg_color': '#C65911', 'border': 1})
    
    data_fmt = workbook.add_format({'border': 1})
    data_center_fmt = workbook.add_format({'border': 1, 'align': 'center'})
    section_fmt = workbook.add_format({'bold': True, 'bg_color': '#E2EFDA', 'border': 1})
    harvester_section_fmt = workbook.add_format({'bold': True, 'bg_color': '#F8CBAD', 'border': 1})

    # Traffic light formats are now explicitly centered so versions look sharp
    status_fmt = {
        "Green": workbook.add_format({'border': 1, 'align': 'center', 'bg_color': '#C6EFCE', 'font_color': '#006100'}),
        "Yellow": workbook.add_format({'border': 1, 'align': 'center', 'bg_color': '#FFEB9C', 'font_color': '#9C5700'}),
        "Red": workbook.add_format({'border': 1, 'align': 'center', 'bg_color': '#FFC7CE', 'font_color': '#9C0006'}),
        "Unknown": data_center_fmt
    }

    worksheet.write(0, 0, "MANAGEMENT SERVER SUMMARY", title_fmt)
    sum_headers = ["Name", "URL", "Rancher Version", "Local K8s Version", "AWS Region", "Backup Operator", "Config Comment"]
    for col, h in enumerate(sum_headers):
        worksheet.write(1, col, h, header_fmt)
    
    curr_row = 2
    for s in server_summaries:
        for col, key in enumerate(sum_headers):
            if key == "Local K8s Version":
                k8s_status = get_k8s_version_status(s[key], f"[{s['Name']}] Local Server")
                worksheet.write(curr_row, col, s[key], status_fmt.get(k8s_status, data_center_fmt))
            elif key == "Rancher Version":
                rancher_status = get_rancher_version_status(s[key], s["Name"])
                worksheet.write(curr_row, col, s[key], status_fmt.get(rancher_status, data_center_fmt))
            else:
                worksheet.write(curr_row, col, s[key], data_fmt)
        curr_row += 1

    curr_row += 2 

    if harvester_clusters:
        worksheet.write(curr_row, 0, "HARVESTER CLUSTERS", harvester_title_fmt)
        curr_row += 1
        
        harvester_headers = ["Cluster Name", "Harvester Version", "Kubernetes Version", "CPU Arch", "Rancher Server", "Comments"]
        for col, h in enumerate(harvester_headers):
            worksheet.write(curr_row, col, h, harvester_header_fmt)
        
        curr_row += 1
        df_harvester = pd.DataFrame(harvester_clusters)
        
        for server in df_harvester['Rancher Server'].unique():
            worksheet.merge_range(curr_row, 0, curr_row, len(harvester_headers)-1, f"Environment: {server}", harvester_section_fmt)
            curr_row += 1
            subset = df_harvester[df_harvester['Rancher Server'] == server]
            for _, r in subset.iterrows():
                worksheet.write(curr_row, 0, r['Cluster Name'], data_fmt)
                
                hv_status = get_harvester_version_status(r['Harvester Version'], r['Cluster Name'])
                worksheet.write(curr_row, 1, r['Harvester Version'], status_fmt.get(hv_status, data_center_fmt))
                
                k8s_status = get_k8s_version_status(r['Kubernetes Version'], r['Cluster Name'])
                worksheet.write(curr_row, 2, r['Kubernetes Version'], status_fmt.get(k8s_status, data_center_fmt))
                
                worksheet.write(curr_row, 3, r['CPU Arch'], data_center_fmt)
                worksheet.write(curr_row, 4, r['Rancher Server'], data_fmt)
                worksheet.write(curr_row, 5, r['Comments'], data_fmt)
                curr_row += 1
            curr_row += 1
            
        curr_row += 1

    if downstream_clusters:
        worksheet.write(curr_row, 0, "MANAGED DOWNSTREAM CLUSTERS", title_fmt)
        curr_row += 1
        
        cluster_headers = [
            "Cluster Name", "Provider Type", "K8s Distribution", 
            "Full K8s Version", "CPU Arch", "Region", "CPU (Cores)", 
            "Memory", "Total Pods", "Comments"
        ]
        
        for col, h in enumerate(cluster_headers):
            worksheet.write(curr_row, col, h, header_fmt)
        
        curr_row += 1
        df_clusters = pd.DataFrame(downstream_clusters)
        for server in df_clusters['Rancher Server'].unique():
            worksheet.merge_range(curr_row, 0, curr_row, len(cluster_headers)-1, f"Environment: {server}", section_fmt)
            curr_row += 1
            subset = df_clusters[df_clusters['Rancher Server'] == server]
            for _, r in subset.iterrows():
                worksheet.write(curr_row, 0, r['Cluster Name'], data_fmt)
                worksheet.write(curr_row, 1, r['Provider Type'], data_fmt)
                worksheet.write(curr_row, 2, r['K8s Distribution'], data_fmt)
                
                k8s_status = get_k8s_version_status(r['Full K8s Version'], r['Cluster Name'])
                worksheet.write(curr_row, 3, r['Full K8s Version'], status_fmt.get(k8s_status, data_center_fmt))
                
                worksheet.write(curr_row, 4, r['CPU Arch'], data_center_fmt)
                worksheet.write(curr_row, 5, r['Region'], data_fmt)
                worksheet.write(curr_row, 6, r['CPU (Cores)'], data_center_fmt)
                worksheet.write(curr_row, 7, r['Memory'], data_center_fmt)
                worksheet.write(curr_row, 8, r['Total Pods'], data_center_fmt)
                worksheet.write(curr_row, 9, r['Comments'], data_fmt)
                curr_row += 1
            curr_row += 1 

    worksheet.set_column(0, 0, 25) 
    worksheet.set_column(1, 2, 28) 
    worksheet.set_column(3, 3, 25) 
    worksheet.set_column(4, 4, 15) 
    worksheet.set_column(5, 5, 15) 
    worksheet.set_column(6, 8, 12) 
    worksheet.set_column(9, 9, 20) 

    writer.close()
    print(f"\n✅ Spreadsheet saved: {filename}")

if __name__ == "__main__":
    config = load_config()
    if config and "rancher_instances" in config:
        instances = config['rancher_instances']
        server_list = [get_server_summary(i) for i in instances]
        regular_clusters, harvester_clusters = get_cluster_data(instances)
        save_styled_excel(server_list, regular_clusters, harvester_clusters)
