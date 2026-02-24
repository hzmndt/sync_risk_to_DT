# Chronicle Risk Config Sync Guide

This script automates the process of fetching Risk Configuration settings from Chronicle and storing them in a Data Table for auditing or lookup.

## Prerequisites

1. **Google Cloud SDK (gcloud)**: Must be installed and authenticated.
   ```bash
   gcloud auth login
   gcloud config set project [YOUR_PROJECT_ID]
   ```
2. **Permissions**: Your authenticated account must have `chronicle.viewer` and `chronicle.editor` roles or equivalent to access Risk Config and Data Tables.
3. **Python 3**: The script uses standard libraries and `curl` for API calls.

## How to Run

1. **Navigate to the script directory**:
   ```bash
   cd /Users/hzmndt/google-ti/gti_release
   ```

2. **Run the script**:
   ```bash
   python3 sync_risk_to_table.py
   ```

## What the Script Does

1. **Fetches** the current Risk Configuration from:
   `https://asia-southeast1-chronicle.googleapis.com/.../riskConfig`
2. **Checks** if a Data Table named `risk_config_storage` exists.
   - If it doesn't exist, it creates it with the appropriate numeric columns.
3. **Inserts** a new row with the current configuration values:
   - `detection_risk_score`
   - `alert_risk_score`
   - `weighting_factor`
   - `closed_alert_coefficient`

## Verification

You can verify the data in the Chronicle UI:
[Risk Config Storage Table](https://gvt-test-asia-southeast1.backstory.chronicle.security/settings/data-tables)
