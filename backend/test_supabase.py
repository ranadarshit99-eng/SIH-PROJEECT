import os
import urllib.request
import json
from dotenv import load_dotenv

load_dotenv()

supabase_url = "https://ifrgbfbqenezaciikalc.supabase.co"
anon_key = os.getenv("SUPABASE_ANON_KEY", "")

headers = {
    "apikey": anon_key,
    "Authorization": f"Bearer {anon_key}"
}

tables = ["bis_details", "msme_details", "gst_details", "pan_details", "iso_details"]

for table in tables:
    try:
        url = f"{supabase_url}/rest/v1/{table}?select=*"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            print(f"Table '{table}': {len(data)} rows")
            if data:
                print(f"  Columns in {table}: {list(data[0].keys())}")
                print(f"  Sample row: {data[0]}")
    except Exception as e:
        print(f"Table '{table}' Error: {e}")
