import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "sih_enterprise.db")
dump_path = os.path.join(os.path.dirname(__file__), "dump.txt")

conn = sqlite3.connect(db_path)
c = conn.cursor()

lines = []
lines.append("=== TABLES ===")
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = c.fetchall()
lines.append(str(tables))

lines.append("\n=== USERS ===")
c.execute("SELECT id, username, email, user_type FROM system_users")
users = c.fetchall()
for u in users:
    lines.append(str(u))

lines.append("\n=== SESSIONS ===")
c.execute("SELECT session_id, user_id, email, is_active FROM auth_sessions")
sessions = c.fetchall()
for s in sessions:
    lines.append(str(s))

with open(dump_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("Dump completed successfully.")
