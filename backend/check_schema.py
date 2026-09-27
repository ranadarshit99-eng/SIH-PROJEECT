import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from sqlalchemy import create_engine, text

db_url = 'postgresql://postgres:D%40RSHIT%2345SIH@db.ifrgbfbqenezaciikalc.supabase.co:5432/postgres'
engine = create_engine(db_url)

with engine.connect() as conn:
    for table in ['itr_details', 'msme_details', 'oem_details', 'turnover_details', 'pan_details']:
        print(f"\n=== SAMPLE DATA from {table} ===")
        try:
            sample = conn.execute(text(f"SELECT * FROM {table} LIMIT 1;")).mappings().all()
            for row in sample:
                for k, v in dict(row).items():
                    vstr = str(v).encode('ascii', errors='replace').decode('ascii')
                    print(f"  {k}: {vstr}")
        except Exception as e:
            print(f"  ERROR: {e}")
