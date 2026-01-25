import requests
import json
import time

url = "https://amazing-river-497.apps.tower.dev/"

# Test case 1: Berlin (Expect Violation)
payload = {
    "address": "Alexanderplatz, Berlin, Germany",
    "text_content": "Modern apartment in the city center."
}

headers = {
    "Content-Type": "application/json"
}

print(f"Sending POST request to {url}...")
print(f"Payload: {json.dumps(payload, indent=2)}")

for i in range(20):
    try:
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 202:
            print(f"App is starting (202), retrying in 3s... ({i+1}/20)")
            time.sleep(3)
            continue
            
        print(f"\nStatus Code: {response.status_code}")
        print("Response Body:")
        try:
            print(json.dumps(response.json(), indent=2))
            break # Success!
        except json.JSONDecodeError:
            print(response.text)
            # If it's HTML, it might still be loading or an error page
            if "<html" in response.text.lower():
                 print("Received HTML instead of JSON. Retrying in 3s...")
                 time.sleep(3)
            else:
                 break
                 
    except Exception as e:
        print(f"An error occurred: {e}")
        time.sleep(3)
