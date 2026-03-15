"""Reset admin user password so admin login works. Run: python reset_admin.py"""
import os
from dotenv import load_dotenv
load_dotenv()

from app import app
from models import db, User

with app.app_context():
    admin_email = os.getenv('ADMIN_EMAIL', 'admin@company.com')
    admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
    admin = User.query.filter_by(email=admin_email, role='admin').first()
    if not admin:
        admin = User(email=admin_email, role='admin')
        admin.set_password(admin_password)
        db.session.add(admin)
        db.session.commit()
        print(f'Created admin: {admin_email} / {admin_password}')
    else:
        admin.set_password(admin_password)
        db.session.commit()
        print(f'Reset password for admin: {admin_email} / {admin_password}')
    print('Done. You can log in with the credentials above.')
