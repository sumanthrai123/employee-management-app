"""
Create PostgreSQL database for the app (employee_management) if it does not exist.
Requires DATABASE_URL in .env or PGPASSWORD when URL has placeholder.
"""
import os
import sys
from urllib.parse import urlparse

from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL or 'postgresql' not in DATABASE_URL.lower():
    print('DATABASE_URL must be set to PostgreSQL in .env. Run run_postgres_setup.bat or set DATABASE_URL.')
    sys.exit(1)

def main():
    try:
        import psycopg2
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
    except ImportError:
        print('psycopg2 is required. Install with: pip install psycopg2-binary')
        sys.exit(1)

    parsed = urlparse(DATABASE_URL)
    host = parsed.hostname or '127.0.0.1'
    port = parsed.port or 5432
    user = parsed.username or 'postgres'
    password = parsed.password or ''
    if not password or password == 'YOUR_PASSWORD' or password == 'YOUR_POSTGRES_PASSWORD':
        password = os.environ.get('PGPASSWORD', '')
    db_name = (parsed.path or '/employee_management').lstrip('/') or 'employee_management'

    conn_params = {
        'host': host,
        'port': port,
        'user': user,
        'password': password,
        'dbname': 'postgres',
    }
    try:
        conn = psycopg2.connect(**conn_params)
    except Exception as e:
        print(f'Could not connect to PostgreSQL at {host}:{port}. Error: {e}')
        print('Ensure PostgreSQL is running and DATABASE_URL (or PGPASSWORD) in .env is correct.')
        sys.exit(1)

    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    try:
        cur.execute(f'CREATE DATABASE "{db_name}"')
        print(f'Database "{db_name}" created.')
    except psycopg2.Error as e:
        if e.pgcode == '42P04' or 'already exists' in str(e).lower():
            print(f'Database "{db_name}" already exists.')
        else:
            print(f'Error creating database: {e}')
            cur.close()
            conn.close()
            sys.exit(1)

    cur.close()
    conn.close()
    print('Done.')

if __name__ == '__main__':
    main()
