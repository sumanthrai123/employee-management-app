"""
Drop duplicate lowercase tables (users, departments, employees) so only
the 3 capitalized tables (Users, Departments, Employees) remain.
Run this once if you see 6 tables in the database.
"""
import os
from dotenv import load_dotenv
load_dotenv()

def main():
    try:
        import psycopg2
    except ImportError:
        print('psycopg2 required: pip install psycopg2-binary')
        return

    url = os.getenv('DATABASE_URL')
    if not url or 'postgresql' not in url.lower():
        print('Set DATABASE_URL in .env to PostgreSQL.')
        return

    from urllib.parse import urlparse
    parsed = urlparse(url)
    conn_params = {
        'host': parsed.hostname or '127.0.0.1',
        'port': parsed.port or 5432,
        'user': parsed.username or 'postgres',
        'password': parsed.password or '',
        'dbname': (parsed.path or '/employee_management').strip('/') or 'employee_management',
    }

    # Drop in order: users (FK to employees), then employees (FK to departments, self), then departments
    tables_to_drop = ['users', 'employees', 'departments']

    try:
        conn = psycopg2.connect(**conn_params)
        conn.autocommit = False
        cur = conn.cursor()
        for name in tables_to_drop:
            cur.execute(
                "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = %s)",
                (name,)
            )
            if cur.fetchone()[0]:
                cur.execute(f'DROP TABLE IF EXISTS "{name}" CASCADE')
                print(f'Dropped: {name}')
            else:
                print(f'Skipped (not found): {name}')
        conn.commit()
        cur.close()
        conn.close()
        print('Done. You should now have only 3 tables: Users, Departments, Employees.')
    except Exception as e:
        print('Error:', e)

if __name__ == '__main__':
    main()
