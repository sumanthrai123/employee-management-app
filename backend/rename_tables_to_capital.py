"""
One-time migration: rename database tables to capital first letter (Users, Departments, Employees).
Run this once if you already have data in the old lowercase tables (users, departments, employees).
If you have a fresh database, just run seed.py and skip this script.
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

    renames = [
        ('users', 'Users'),
        ('departments', 'Departments'),
        ('employees', 'Employees'),
    ]

    try:
        conn = psycopg2.connect(**conn_params)
        conn.autocommit = False
        cur = conn.cursor()
        # If capitalized tables already exist (empty), drop them so we can rename lowercase -> capital
        for _old, new_name in renames:
            cur.execute(
                'SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = %s AND table_name = %s)',
                ('public', new_name)
            )
            if cur.fetchone()[0]:
                cur.execute(f'DROP TABLE IF EXISTS "{new_name}" CASCADE')
                print(f'Dropped existing (empty): {new_name}')
        for old_name, new_name in renames:
            cur.execute(
                'SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = %s AND table_name = %s)',
                ('public', old_name)
            )
            if cur.fetchone()[0]:
                cur.execute(f'ALTER TABLE "{old_name}" RENAME TO "{new_name}"')
                print(f'Renamed: {old_name} -> {new_name}')
            else:
                print(f'Skipped (not found): {old_name}')
        conn.commit()
        cur.close()
        conn.close()
        print('Done.')
    except Exception as e:
        print('Error:', e)

if __name__ == '__main__':
    main()
