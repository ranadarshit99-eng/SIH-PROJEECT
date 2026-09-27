import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from main import app
from fastapi.testclient import TestClient

client = TestClient(app)
out = []

out.append("--- 1. Testing Home Endpoint ---")
r_home = client.get("/")
out.append(f"Home: {r_home.status_code} {r_home.json()}")

out.append("\n--- 2. Testing Register User ---")
reg_payload = {
    "user_type": "bidder",
    "username": "apex_builder_2026",
    "email": "contact@apexbuilder.com",
    "password": "Password@123",
    "full_name": "Apex Builders & Infra",
    "organization": "Apex Infrastructure Group",
    "gstin": "27APEXB1234A1Z0"
}
r_reg = client.post("/auth/register", json=reg_payload)
out.append(f"Register Status: {r_reg.status_code}")
out.append(f"Register Response: {r_reg.json()}")

session_id = r_reg.json().get("session_id")

out.append("\n--- 3. Testing Auth Me Endpoint ---")
r_me = client.get("/auth/me", headers={"Authorization": f"Bearer {session_id}"})
out.append(f"Me Status: {r_me.status_code}")
out.append(f"Me Response: {r_me.json()}")

out.append("\n--- 4. Testing Login Endpoint ---")
login_payload = {
    "email_or_username": "apex_builder_2026",
    "password": "Password@123",
    "user_type": "bidder"
}
r_login = client.post("/auth/login", json=login_payload)
out.append(f"Login Status: {r_login.status_code}")
out.append(f"Login Response: {r_login.json()}")

out.append("\n--- 5. Testing Fetch All Tenders ---")
r_tenders = client.get("/tenders/all")
out.append(f"Tenders Status: {r_tenders.status_code}")
out.append(f"Tenders Count: {r_tenders.json().get('count')}")

out.append("\n--- 6. Testing Active Sessions Audit ---")
r_sess = client.get("/auth/active-sessions")
out.append(f"Active Sessions Status: {r_sess.status_code}")
out.append(f"Active Sessions Total: {r_sess.json().get('total_sessions')}")

res_file = os.path.join(os.path.dirname(__file__), "test_results.txt")
with open(res_file, "w", encoding="utf-8") as f:
    f.write("\n".join(out))

print(f"Results written to {res_file}")
