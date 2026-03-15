"""Create DB tables, admin, departments, and sample employees + one employee login."""
import os
from datetime import date, timedelta
from app import app
from models import db, User, Department, Employee

with app.app_context():
    db.create_all()

    # Admin
    admin_email = os.getenv('ADMIN_EMAIL', 'admin@company.com')
    admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
    admin = User.query.filter_by(email=admin_email, role='admin').first()
    if not admin:
        admin = User(email=admin_email, role='admin')
        db.session.add(admin)
    admin.set_password(admin_password)
    print(f'Admin: {admin_email} / {admin_password}')

    # Departments
    dept_names = ['IT', 'HR', 'Finance', 'Marketing', 'Operations']
    depts = {}
    for name in dept_names:
        d = Department.query.filter_by(name=name).first()
        if not d:
            d = Department(name=name)
            db.session.add(d)
            db.session.flush()
        depts[name] = d
    db.session.commit()

    # Sample employees with org hierarchy (CEO -> VP -> Manager -> Employee)
    def add_emp(eid, first, last, email, job_title, dept_name, manager_id=None, salary=None, gender=None, date_joined=None):
        if Employee.query.filter_by(employee_id=eid).first():
            return Employee.query.filter_by(employee_id=eid).first()
        d = depts.get(dept_name)
        emp = Employee(
            employee_id=eid,
            first_name=first,
            last_name=last,
            email=email,
            job_title=job_title,
            department_id=d.id if d else None,
            manager_id=manager_id,
            salary=salary,
            gender=gender,
            date_joined=date_joined or date.today() - timedelta(days=365),
        )
        db.session.add(emp)
        db.session.flush()
        return emp

    # Ensure we have departments with ids
    db.session.commit()
    depts = {d.name: d for d in Department.query.all()}

    ceo = add_emp('EMP001', 'Alex', 'Morgan', 'alex.morgan@company.com', 'CEO', 'Operations', None, 250000, 'Male', date(2020, 1, 15))
    vp1 = add_emp('EMP002', 'Jordan', 'Lee', 'jordan.lee@company.com', 'VP Engineering', 'IT', ceo.id, 180000, 'Female', date(2020, 3, 1))
    vp2 = add_emp('EMP003', 'Sam', 'Davis', 'sam.davis@company.com', 'VP Human Resources', 'HR', ceo.id, 170000, 'Male', date(2020, 4, 1))
    mgr1 = add_emp('EMP004', 'Casey', 'Brown', 'casey.brown@company.com', 'Engineering Manager', 'IT', vp1.id, 120000, 'Female', date(2021, 1, 10))
    mgr2 = add_emp('EMP005', 'Riley', 'Wilson', 'riley.wilson@company.com', 'HR Manager', 'HR', vp2.id, 95000, 'Male', date(2021, 2, 1))
    add_emp('EMP006', 'John', 'Smith', 'john.smith@company.com', 'Software Engineer', 'IT', mgr1.id, 85000, 'Male', date(2022, 6, 1))
    add_emp('EMP007', 'Jane', 'Doe', 'jane.doe@company.com', 'Software Engineer', 'IT', mgr1.id, 82000, 'Female', date(2022, 8, 15))
    add_emp('EMP008', 'Mike', 'Johnson', 'mike.johnson@company.com', 'HR Specialist', 'HR', mgr2.id, 65000, 'Male', date(2023, 1, 10))
    add_emp('EMP009', 'Sarah', 'Williams', 'sarah.williams@company.com', 'Finance Analyst', 'Finance', ceo.id, 72000, 'Female', date(2023, 3, 1))
    add_emp('EMP010', 'Chris', 'Taylor', 'chris.taylor@company.com', 'Marketing Lead', 'Marketing', ceo.id, 78000, 'Other', date(2022, 11, 1))

    db.session.commit()

    # One employee user for login (john.smith@company.com / employee123)
    john = Employee.query.filter_by(email='john.smith@company.com').first()
    if john:
        u = User.query.filter_by(email='john.smith@company.com').first()
        if not u:
            u = User(email='john.smith@company.com', role='employee', employee_id=john.id)
            db.session.add(u)
        u.set_password('employee123')
        db.session.commit()
        print('Employee login: john.smith@company.com / employee123')

    print('Seed complete. Sample data: users (1 admin, 1 employee), departments (5), employees (10).')
