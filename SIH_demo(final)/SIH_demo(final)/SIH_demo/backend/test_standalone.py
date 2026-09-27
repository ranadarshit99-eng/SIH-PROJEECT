import os
import sys
import json

sys.path.insert(0, os.path.dirname(__file__))

from database import engine, SessionLocal
from create_auth_tables import init_auth_tables, hash_password
from routers.auth import RegisterRequest, register_user, LoginRequest, login_user
from sqlalchemy import text

out_path = os.path.join(os.path.dirname(__file__), "standalone_results.txt")

with open(out_path, "w", encoding="utf-8") as out:
    out.write("--- Step 1. Initializing Auth Tables ---\n")
    init_auth_tables()
    out.write("Tables initialized!\n\n")

    out.write("--- Step 2. Registering New User ---\n")
    reg_req = RegisterRequest(
        user_type="bidder",
        username="enterprise_vendor_100",
        email="vendor100@enterprise.com",
        password="Password@123",
        full_name="Enterprise Vendor Ltd",
        organization="Enterprise Group",
        gstin="27ENTPV1234A1Z1"
    )

    class MockRequest:
        class client:
            host = "127.0.0.1"
        headers = {}

    class MockResponse:
        def set_cookie(self, **kwargs):
            pass

    try:
        reg_res = register_user(reg_req, MockRequest(), MockResponse())
        out.write(f"Register Success! Result: {json.dumps(reg_res, indent=2)}\n\n")
    except Exception as e:
        out.write(f"Register Error: {e}\n\n")

    out.write("--- Step 3. Testing Login ---\n")
    login_req = LoginRequest(
        email_or_username="enterprise_vendor_100",
        password="Password@123",
        user_type="bidder"
    )
    try:
        login_res = login_user(login_req, MockRequest(), MockResponse())
        out.write(f"Login Success! Result: {json.dumps(login_res, indent=2)}\n\n")
    except Exception as e:
        out.write(f"Login Error: {e}\n\n")

    out.write("--- Step 4. Querying Users & Sessions ---\n")
    db = SessionLocal()
    users = db.execute(text("SELECT id, username, email, user_type FROM system_users")).fetchall()
    out.write(f"Users in DB: {users}\n")

    sessions = db.execute(text("SELECT session_id, user_id, email, is_active FROM auth_sessions")).fetchall()
    out.write(f"Sessions in DB: {sessions}\n")
    db.close()

print(f"DONE. Results saved to {out_path}")
