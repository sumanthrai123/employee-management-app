import os
from dotenv import load_dotenv
load_dotenv()
import psycopg2
from urllib.parse import urlparse
url = os.getenv('DATABASE_URL')
parsed = urlparse(url)
conn = psycopg2.connect(
    host=parsed.hostname or '127.0.0.1',
    port=parsed.port or 5432,
    user=parsed.username or 'postgres',
    password=parsed.password or '',
    dbname=(parsed.path or '/employee_management').strip('/') or 'employee_management',
)
cur = conn.cursor()
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name")
rows = cur.fetchall()
print('Tables:', [r[0] for r in rows])
cur.close()
conn.close()
