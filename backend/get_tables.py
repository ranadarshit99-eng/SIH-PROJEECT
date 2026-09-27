import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect

load_dotenv()
db_url = os.getenv("DATABASE_URL")
if not db_url:
    db_url = 'postgresql://postgres:D%40RSHIT%2345SIH@db.ifrgbfbqenezaciikalc.supabase.co:5432/postgres'

engine = create_engine(db_url)
inspector = inspect(engine)
tables = inspector.get_table_names()
print("TABLES IN DATABASE:")
for t in sorted(tables):
    print(" -", t)
