import urllib.request
import json

url = "https://ifrgbfbqenezaciikalc.supabase.co/rest/v1/"
req = urllib.request.Request(url)
try:
    with urllib.request.urlopen(req, timeout=5) as resp:
        print("REST Status:", resp.status)
        print("REST Response:", resp.read().decode())
except Exception as e:
    print("REST Error:", e)
