import requests
import json

url = "http://127.0.0.1:8000/cross-engine/evaluate"

payload = {
    "submission_id": "sub_test_001",
    "tender_schema": {
        "fields": [
            {"id": "gst", "type": "file", "required": True, "label": "GST Certificate"},
            {"id": "pan", "type": "file", "required": True, "label": "PAN Card"},
            {"id": "msme", "type": "file", "required": False, "label": "MSME Certificate"}
        ]
    },
    "verifications_map": {
        "gst": {
            "data": {
                "gstin": "27AAACB1234A1Z5",
                "legal_name": "Tata Infrastructure Pvt Ltd"
            }
        },
        "pan": {
            "data": {
                "pan": "AACB1234A",
                "name": "Tata Infrastructure Pvt Ltd"
            }
        }
    },
    "form_data": {}
}

print("Sending request to Cross-Engine...")
try:
    res = requests.post(url, json=payload)
    print("STATUS CODE:", res.status_code)
    print("RESPONSE JSON:")
    print(json.dumps(res.json(), indent=2))
except Exception as e:
    print("ERROR:", e)
