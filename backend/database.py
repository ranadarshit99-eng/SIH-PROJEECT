import os
import sys
import socket
import threading
from urllib.parse import urlparse
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = None

def is_postgres_reachable(url_str: str, timeout: float = 2.5) -> bool:
    """Non-blocking check to test if PostgreSQL host is reachable (allowing cloud latency for Supabase)."""
    result = [False]
    def _check():
        try:
            parsed = urlparse(url_str)
            host = parsed.hostname
            port = parsed.port or 5432
            if not host:
                return
            with socket.create_connection((host, port), timeout=timeout):
                result[0] = True
        except Exception:
            pass

    t = threading.Thread(target=_check, daemon=True)
    t.start()
    t.join(timeout)
    return result[0]

# Default USE_POSTGRES to true if DATABASE_URL is present
USE_POSTGRES = os.getenv("USE_POSTGRES", "true").lower() in ("1", "true", "yes")

if USE_POSTGRES and DATABASE_URL and DATABASE_URL.strip() and is_postgres_reachable(DATABASE_URL, timeout=2.5):
    try:
        temp_engine = create_engine(
            DATABASE_URL,
            connect_args={"connect_timeout": 5},
            pool_pre_ping=True,
            pool_recycle=300
        )
        with temp_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        engine = temp_engine
        print("[Database] Connected successfully to remote PostgreSQL.")
    except Exception as e:
        print(f"[Database Warning] PostgreSQL connection check failed: {e}")
        engine = None

# High-performance local SQLite engine for sub-millisecond local response times
if engine is None:
    SQLITE_URL = "sqlite:///./sih_enterprise.db"
    engine = create_engine(
        SQLITE_URL,
        connect_args={"check_same_thread": False},
        pool_pre_ping=True
    )
    try:
        with engine.begin() as conn:
            conn.execute(text("PRAGMA journal_mode=WAL;"))
            conn.execute(text("PRAGMA synchronous=NORMAL;"))
    except Exception as e:
        pass
    print("[Database] Connected to high-speed local SQLite database (sih_enterprise.db).")

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)