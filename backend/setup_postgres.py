"""
One-time setup: prompt for your PostgreSQL password, create the database, update .env, and seed.
Run: python setup_postgres.py
"""
import os
import sys

# Load current .env
from dotenv import load_dotenv
load_dotenv()

def main():
    try:
        from getpass import getpass
    except ImportError:
        getpass = lambda p: input(p)

    url = os.getenv('DATABASE_URL', '')
    password = os.environ.get('PGPASSWORD')
    if not url or 'postgresql' not in url.lower():
        url = 'postgresql://postgres:POSTGRES_PASSWORD@127.0.0.1:5432/employee_management'
    if password:
        print('Using PGPASSWORD from environment.')
    else:
        from urllib.parse import urlparse
        p = urlparse(url) if url else None
        if p and getattr(p, 'password', None) and p.password not in ('', 'POSTGRES_PASSWORD', 'postgres'):
            print('DATABASE_URL already has a password. Attempting to create DB and seed...')
            run_create_and_seed(url)
            return
        if not password:
            password = getpass('PostgreSQL password for user "postgres": ')
    if not password and not os.environ.get('PGPASSWORD'):
        print('No password entered. Set PGPASSWORD or run again and enter password.')
        sys.exit(1)
    if not password:
        password = os.environ.get('PGPASSWORD')

    # Build URL with password (quote if needed)
    from urllib.parse import urlparse, quote_plus
    if url.startswith('postgresql://') or url.startswith('postgres://'):
        p = urlparse(url)
        safe = quote_plus(password)
        new_url = f'postgresql://{p.username}:{safe}@{p.hostname or "127.0.0.1"}:{p.port or 5432}/{p.path.lstrip("/") or "employee_management"}'
    else:
        new_url = f'postgresql://postgres:{quote_plus(password)}@127.0.0.1:5432/employee_management'

    run_create_and_seed(new_url, update_env=True)

def run_create_and_seed(database_url, update_env=False):
    from urllib.parse import urlparse
    import subprocess

    env = os.environ.copy()
    env['DATABASE_URL'] = database_url

    # Create DB via Python
    parsed = urlparse(database_url)
    host = parsed.hostname or '127.0.0.1'
    port = parsed.port or 5432
    user = parsed.username or 'postgres'
    password = parsed.password or ''
    db_name = (parsed.path or '/employee_management').lstrip('/') or 'employee_management'

    try:
        import psycopg2
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
    except ImportError:
        print('Install psycopg2-binary: pip install psycopg2-binary')
        sys.exit(1)

    try:
        conn = psycopg2.connect(
            host=host, port=port, user=user, password=password,
            dbname='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        try:
            cur.execute(f'CREATE DATABASE "{db_name}"')
            print(f'Database "{db_name}" created.')
        except psycopg2.Error as e:
            if e.pgcode == '42P04' or 'already exists' in str(e).lower():
                print(f'Database "{db_name}" already exists.')
            else:
                raise
        cur.close()
        conn.close()
    except Exception as e:
        print(f'PostgreSQL connection failed: {e}')
        print('Check that PostgreSQL is running and the password is correct.')
        sys.exit(1)

    if update_env:
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        lines = []
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    if line.strip().startswith('DATABASE_URL='):
                        lines.append(f'DATABASE_URL={database_url}\n')
                        continue
                    lines.append(line)
        if not any(l.strip().startswith('DATABASE_URL=') for l in lines):
            lines.append(f'DATABASE_URL={database_url}\n')
        with open(env_path, 'w') as f:
            f.writelines(lines)
        print('Updated .env with DATABASE_URL.')

    # Seed (must run with DATABASE_URL set)
    os.environ['DATABASE_URL'] = database_url
    print('Creating tables and seeding admin + departments...')
    from app import app
    from models import db, User, Department, Employee

    with app.app_context():
        db.create_all()
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@company.com')
        admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
        admin = User.query.filter_by(email=admin_email, role='admin').first()
        if not admin:
            admin = User(email=admin_email, role='admin')
            db.session.add(admin)
        admin.set_password(admin_password)
        for name in ['IT', 'HR', 'Finance', 'Marketing', 'Operations']:
            if not Department.query.filter_by(name=name).first():
                db.session.add(Department(name=name))
        db.session.commit()
    print('Done. You can run: python app.py')

if __name__ == '__main__':
    main()
