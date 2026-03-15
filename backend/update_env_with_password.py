"""Write DATABASE_URL to .env using PGPASSWORD. Used by run_postgres_setup.bat."""
import os
from pathlib import Path
from urllib.parse import quote_plus

pwd = os.environ.get('PGPASSWORD', '')
if not pwd:
    print('PGPASSWORD not set.')
    exit(1)
url = 'postgresql://postgres:' + quote_plus(pwd) + '@127.0.0.1:5432/employee_management'
p = Path(__file__).parent / '.env'
if p.exists():
    lines = []
    done = False
    for line in p.read_text().splitlines():
        if line.strip().startswith('DATABASE_URL='):
            lines.append('DATABASE_URL=' + url)
            done = True
        else:
            lines.append(line)
    if not done:
        lines.append('DATABASE_URL=' + url)
    p.write_text('\n'.join(lines) + '\n')
else:
    p.write_text('DATABASE_URL=' + url + '\n')
print('Updated .env with DATABASE_URL.')
