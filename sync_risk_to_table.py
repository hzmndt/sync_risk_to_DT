import subprocess
import json
import sys
import argparse

# Configuration
PROJECT = "678335183637"
LOCATION = "asia-southeast1"
INSTANCE = "08189574-f559-4428-92dd-0314f7723c6f"
TABLE_ID = "risk_config_storage"

def get_access_token():
    try:
        token = subprocess.check_output(["gcloud", "auth", "print-access-token"]).decode().strip()
        return token
    except Exception as e:
        print(f"Error getting access token: {e}")
        sys.exit(1)

def activate_service_account(key_file):
    try:
        print(f"Activating service account with key file: {key_file}")
        subprocess.check_call(["gcloud", "auth", "activate-service-account", "--key-file", key_file])
    except Exception as e:
        print(f"Error activating service account: {e}")
        sys.exit(1)

def api_call(url, method="GET", body=None):
    token = get_access_token()
    headers = [
        "-H", f"Authorization: Bearer {token}",
        "-H", "Content-Type: application/json"
    ]
    cmd = ["curl", "-s", "-X", method, url] + headers
    if body:
        cmd += ["-d", json.dumps(body)]
    
    try:
        output = subprocess.check_output(cmd).decode()
        if not output:
            return {}
        return json.loads(output)
    except Exception as e:
        print(f"Error in API call to {url}: {e}")
        return None

def sync_risk_config():
    parser = argparse.ArgumentParser(description="Sync Chronicle Risk Config to Data Table")
    parser.add_argument("--key-file", help="Path to the service account JSON key file")
    args = parser.parse_args()

    if args.key_file:
        activate_service_account(args.key_file)

    base_url = f"https://{LOCATION}-chronicle.googleapis.com/v1alpha/projects/{PROJECT}/locations/{LOCATION}/instances/{INSTANCE}"
    
    # 1. Fetch Risk Config
    print("Fetching Risk Config...")
    risk_config_url = f"{base_url}/riskConfig"
    config = api_call(risk_config_url)
    if not config or "defaultDetectionRiskScore" not in config:
        print("Failed to fetch Risk Config.")
        if config and "error" in config:
            print(f"Error: {config['error']['message']}")
        return

    row_data = [
        config.get("defaultDetectionRiskScore", 0),
        config.get("defaultAlertRiskScore", 0),
        config.get("defaultWeightingFactor", 0),
        config.get("defaultClosedAlertCoefficient", 0)
    ]
    print(f"Found Config: {row_data}")

    # 2. Check if Data Table exists, create if not
    print(f"Ensuring Data Table '{TABLE_ID}' exists...")
    table_url = f"{base_url}/dataTables/{TABLE_ID}"
    table_status = api_call(table_url)
    
    if table_status and "error" in table_status and table_status["error"]["code"] == 404:
        print("Table not found. Creating...")
        create_url = f"{base_url}/dataTables?dataTableId={TABLE_ID}"
        schema = {
            "displayName": "Risk Config Storage",
            "description": "Stores chronicle risk configuration settings",
            "columnInfo": [
                {"columnIndex": 0, "originalColumn": "detection_risk_score", "columnType": "NUMBER"},
                {"columnIndex": 1, "originalColumn": "alert_risk_score", "columnType": "NUMBER"},
                {"columnIndex": 2, "originalColumn": "weighting_factor", "columnType": "NUMBER"},
                {"columnIndex": 3, "originalColumn": "closed_alert_coefficient", "columnType": "NUMBER"}
            ]
        }
        create_res = api_call(create_url, method="POST", body=schema)
        if "error" in create_res:
             print(f"Error creating table: {create_res['error']['message']}")
             return
        print("Table created successfully.")
    else:
        print("Table already exists.")

    # 3. Insert Row
    print("Inserting data row...")
    insert_url = f"{base_url}/dataTables/{TABLE_ID}/dataTableRows"
    row_body = {"values": [str(v) for v in row_data]}
    insert_res = api_call(insert_url, method="POST", body=row_body)
    
    if insert_res and "name" in insert_res:
        print(f"Successfully synced Risk Config to Data Table at {insert_res['createTime']}")
    else:
        print(f"Failed to insert row: {insert_res}")

if __name__ == "__main__":
    sync_risk_config()
