"""Print current DB contents from command prompt. Run: python list_db.py"""
from app import app
from models import User, Department, Employee

with app.app_context():
    print("=== DEPARTMENTS ===")
    for d in Department.query.all():
        print(f"  {d.id}: {d.name}")
    print("\n=== EMPLOYEES (id, employee_id, name, email, job_title, department, manager_id) ===")
    for e in Employee.query.order_by(Employee.employee_id).all():
        dept = e.department.name if e.department else "-"
        print(f"  {e.id}: {e.employee_id} | {e.first_name} {e.last_name} | {e.email} | {e.job_title} | {dept} | manager_id={e.manager_id}")
    print("\n=== USERS (id, email, role, employee_id) ===")
    for u in User.query.all():
        print(f"  {u.id}: {u.email} | {u.role} | employee_id={u.employee_id}")
