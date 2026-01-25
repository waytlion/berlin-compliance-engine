import requests
import json
import time

key = "sk-placeholder-key"
url = "https://api.tower.dev/v1/apps/compliance-check/runs"

headers = {
    "X-API-Key": key,
    "Content-Type": "application/json"
}

# Payload simulating a "Primary Residence > 50%" scenario
payload = {
    "environment": "default",
    "parameters": {
        "address": "Torstraße 1, 10119 Berlin, Germany",
        "property_info": """
            Property Type: Apartment
            Primary Residence: Yes (I live here)
            Entire Unit: Yes, I rent out the whole place while I travel (more than 50%)
            Rented Area: 100%
            Listing Type: Entire Place
            Registration Number: NOT PROVIDED
        """
    }
}

print(f"Triggering Data-Driven compliance check (Verbosity Verification)...")
try:
    response = requests.post(url, headers=headers, json=payload, timeout=10)
    print(f"Start Status: {response.status_code}")
    
    if response.status_code == 201:
        data = response.json()
        run_number = data['run']['number']
        print(f"Run #{run_number} started. Check logs for DETAILED explanations.")
    else:
        print(f"Error starting run: {response.text}")

except Exception as e:
    print(f"Error: {e}")
