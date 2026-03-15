import os
from dotenv import load_dotenv

load_dotenv()

# PostgreSQL only. Set DATABASE_URL in .env (required).
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL or 'postgresql' not in DATABASE_URL.lower():
    raise ValueError(
        'DATABASE_URL must be set to PostgreSQL in .env. '
        'Run run_postgres_setup.bat or set: postgresql://postgres:YOUR_PASSWORD@127.0.0.1:5432/employee_management'
    )
if 'YOUR_PASSWORD' in (DATABASE_URL or '') or 'YOUR_POSTGRES_PASSWORD' in (DATABASE_URL or ''):
    raise ValueError(
        'Replace YOUR_PASSWORD in DATABASE_URL (in .env) with your PostgreSQL password, or run run_postgres_setup.bat'
    )

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    # Must be set and stable so tokens work after restart
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY') or 'emp-mgmt-jwt-secret-key-32chars-long-fixed'
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ACCESS_TOKEN_EXPIRES = 604800  # 7 days
    JWT_ALGORITHM = 'HS256'
