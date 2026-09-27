import database
from sqlalchemy import text

print("Current active database engine:", database.engine)
with database.engine.connect() as conn:
    res = conn.execute(text("SELECT current_database(), current_user;")).fetchone()
    print("Connected database & user:", res)
    
    count = conn.execute(text("SELECT count(*) FROM tender_submissions;")).scalar()
    print("Current submissions count in Supabase Postgres 'tender_submissions' table:", count)
