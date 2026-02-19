import requests
import urllib3
import yaml
import os
import shutil
from datetime import datetime

# Disabling SSL warnings for Rancher instances with self-signed certs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CONFIG_FILE = "config.yaml"

def load_config(filepath=CONFIG_FILE):
    """Loads Rancher credentials from the YAML file."""
    if not os.path.exists(filepath):
        print(f"❌ Error: Configuration file '{filepath}' not found.")
        return None
    try:
        with open(filepath, 'r') as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as exc:
        print(f"❌ Error parsing YAML file: {exc}")
        return None

def save_config(config_data, filepath=CONFIG_FILE):
    """Backs up the old config, then saves the new one with custom formatting."""
    
    # 1. Create a timestamped backup of the existing file
    if os.path.exists(filepath):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{filepath}.{timestamp}.bak"
            shutil.copy2(filepath, backup_path)
            print(f"🛡️ Backup of previous config saved to: {backup_path}")
        except Exception as e:
            print(f"⚠️ Warning: Failed to create backup file: {e}")
            # If we can't backup, it might be safer to abort the save, 
            # but we'll proceed since tokens have already been rotated in Rancher.

    # 2. Write the new configuration to the file
    try:
        with open(filepath, 'w') as f:
            f.write("rancher_instances:\n")
            
            for instance in config_data.get('rancher_instances', []):
                f.write("\n")
                f.write(f"  - name: \"{instance.get('name', '')}\"\n")
                f.write(f"    url: \"{instance.get('url', '')}\"\n")
                f.write(f"    token: \"{instance.get('token', '')}\"\n")
                
                if 'comment' in instance:
                    f.write(f"    comment: \"{instance.get('comment', '')}\"\n")
                
                for key, value in instance.items():
                    if key not in ['name', 'url', 'token', 'comment']:
                        f.write(f"    {key}: \"{value}\"\n")
                        
        print(f"✅ Successfully updated {filepath} with new tokens.")
    except Exception as e:
        print(f"❌ Error saving new configuration: {e}")

def rotate_tokens(config_data):
    """Rotates tokens for all instances in the config data."""
    instances = config_data.get('rancher_instances', [])
    
    if not instances:
        print("No instances found in configuration.")
        return False

    changes_made = False

    for instance in instances:
        name = instance.get('name', 'Unknown Instance')
        url = instance.get('url', '').rstrip('/')
        old_bearer_token = instance.get('token', '')

        if not url or not old_bearer_token:
            print(f"⚠️ Skipping {name}: Missing URL or Token in config.")
            continue

        print(f"\n🔄 Initiating rotation for: {name}...")
        headers = {"Authorization": f"Bearer {old_bearer_token}"}
        
        # Create the new token (30-day expiration)
        create_url = f"{url}/v3/tokens"
        payload = {
            "type": "token",
            "description": "Auto-Rotated Script Token",
            "ttl": 2592000000 
        }

        try:
            print("   -> Requesting new token...")
            resp = requests.post(create_url, headers=headers, json=payload, verify=False, timeout=10)
            resp.raise_for_status()
            
            new_token_data = resp.json()
            token_id = new_token_data.get('id')
            token_secret = new_token_data.get('token')
            
            if ':' not in token_secret:
                new_bearer_token = f"{token_id}:{token_secret}"
            else:
                new_bearer_token = token_secret

            # Verify the new token works
            print("   -> Verifying new token...")
            verify_headers = {"Authorization": f"Bearer {new_bearer_token}"}
            verify_resp = requests.get(f"{url}/v3/users?me=true", headers=verify_headers, verify=False, timeout=10)
            verify_resp.raise_for_status()

            # Update memory
            instance['token'] = new_bearer_token
            changes_made = True
            print("   -> Token successfully rotated in memory.")

            # Revoke the old token
            old_token_id = old_bearer_token.split(':')[0]
            revoke_url = f"{url}/v3/tokens/{old_token_id}"
            
            print(f"   -> Revoking old token ({old_token_id})...")
            revoke_resp = requests.delete(revoke_url, headers=verify_headers, verify=False, timeout=10)
            
            if revoke_resp.status_code in [200, 204]:
                print("   -> Old token safely destroyed.")
            else:
                print(f"   ⚠️ Warning: Failed to delete old token. Status Code: {revoke_resp.status_code}")

        except Exception as e:
            print(f"❌ Error rotating token for {name}: {e}")

    return changes_made

if __name__ == "__main__":
    print("Starting Rancher Token Rotation Script...")
    
    config = load_config()
    
    if config:
        if rotate_tokens(config):
            save_config(config)
        else:
            print("\nNo tokens were updated.")
