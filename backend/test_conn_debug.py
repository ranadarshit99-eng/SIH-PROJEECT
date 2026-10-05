import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv("d:/Desktop/SIH_demo(grand final)/backend/.env")

db_url = os.getenv("DATABASE_URL", "postgresql://postgres:D%40RSHIT%2345SIH@db.ifrgbfbqenezaciikalc.supabase.co:5432/postgres")
print("Testing URL:", db_url)

try:
    engine = create_engine(db_url, connect_args={"connect_timeout": 10})
    with engine.connect() as conn:
        res = conn.execute(text("SELECT version();")).scalar()
        print("SUCCESS! Database version:", res)
except Exception as e:
    print("FAILED with error:", e)
