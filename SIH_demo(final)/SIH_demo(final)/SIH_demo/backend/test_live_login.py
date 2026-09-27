import requests

url = "http://127.0.0.1:8000/auth/login"
payload = {
    "email_or_username": "bids@tatainfra.com",
    "password": "Bidder@123",
    "user_type": "bidder"
}

try:
    res = requests.post(url, json=payload)
    print("STATUS:", res.status_code)
    print("RESPONSE:", res.json())
except Exception as e:
    print("ERROR:", e)
