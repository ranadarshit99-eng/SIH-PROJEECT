from sqlalchemy import create_engine, text

db_url = 'postgresql://postgres:D%40RSHIT%2345SIH@db.ifrgbfbqenezaciikalc.supabase.co:5432/postgres'
engine = create_engine(db_url)

TABLES = ['bis_details', 'annexure_details']

with engine.connect() as conn:
    for table in TABLES:
        print(f'\n=== COLUMNS of {table} ===')
        try:
            col_result = conn.execute(text(f"""
                SELECT column_name, data_type 
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = '{table}'
                ORDER BY ordinal_position;
            """))
            rows = col_result.fetchall()
            if rows:
                for row in rows:
                    print(f'  {row[0]} ({row[1]})')
            else:
                print('  (table not found or has no columns)')
        except Exception as e:
            print(f'  ERROR: {e}')
