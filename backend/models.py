from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin' or 'employee'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    employee_id = db.Column(db.Integer, db.ForeignKey('Employees.id'), nullable=True)  # link to employee for employee role

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'role': self.role,
            'employee_id': self.employee_id,
        }


class Department(db.Model):
    __tablename__ = 'Departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    employees = db.relationship('Employee', backref='department', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'employee_count': len(self.employees) if self.employees else 0,
        }


class Employee(db.Model):
    __tablename__ = 'Employees'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(20), unique=True, nullable=False)  # e.g. EMP001
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    gender = db.Column(db.String(20))  # Male, Female, Other
    date_of_birth = db.Column(db.Date)
    address = db.Column(db.String(255))
    job_title = db.Column(db.String(100))
    department_id = db.Column(db.Integer, db.ForeignKey('Departments.id'))
    manager_id = db.Column(db.Integer, db.ForeignKey('Employees.id'))  # reports to
    salary = db.Column(db.Numeric(12, 2))
    date_joined = db.Column(db.Date, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Self-referential: subordinates
    subordinates = db.relationship('Employee', backref=db.backref('manager', remote_side=[id]), lazy=True)
    user = db.relationship('User', backref='employee', uselist=False)

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': f'{self.first_name} {self.last_name}',
            'email': self.email,
            'phone': self.phone,
            'gender': self.gender,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'address': self.address,
            'job_title': self.job_title,
            'department_id': self.department_id,
            'department_name': self.department.name if self.department else None,
            'manager_id': self.manager_id,
            'manager_name': f'{self.manager.first_name} {self.manager.last_name}' if self.manager else None,
            'salary': float(self.salary) if self.salary else None,
            'date_joined': self.date_joined.isoformat() if self.date_joined else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def to_org_node(self):
        """For org tree: id, name, title, children"""
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'name': f'{self.first_name} {self.last_name}',
            'job_title': self.job_title or '',
            'department': self.department.name if self.department else '',
            'children': [e.to_org_node() for e in self.subordinates],
        }
