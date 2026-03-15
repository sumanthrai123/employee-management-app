from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from functools import wraps
from datetime import datetime
from sqlalchemy import or_, func, cast, Integer
from models import db, Employee, Department, User

employees_bp = Blueprint('employees', __name__)

def admin_required():
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            if get_jwt().get('role') != 'admin':
                return jsonify({'error': 'Admin only'}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def get_employee_or_self():
    """Allow admin or the employee themselves (by employee_id claim)."""
    claims = get_jwt()
    if claims.get('role') == 'admin':
        return None
    return claims.get('employee_id')

@employees_bp.route('', methods=['GET'])
@jwt_required()
def list_employees():
    self_emp_id = get_employee_or_self()
    if self_emp_id is not None:
        emp = Employee.query.filter_by(id=self_emp_id).first()
        if not emp:
            return jsonify({'error': 'Employee not found'}), 404
        return jsonify([emp.to_dict()])
    # Admin: search and filter
    q = Employee.query
    search = request.args.get('search', '').strip()
    if search:
        like = f'%{search}%'
        q = q.filter(
            or_(
                Employee.employee_id.ilike(like),
                Employee.first_name.ilike(like),
                Employee.last_name.ilike(like),
                Employee.email.ilike(like),
                Employee.job_title.ilike(like),
                Employee.phone.ilike(like),
            )
        )
    department_id = request.args.get('department_id', type=int)
    if department_id:
        q = q.filter(Employee.department_id == department_id)
    gender = request.args.get('gender', '').strip()
    if gender:
        q = q.filter(Employee.gender == gender)
    # Sort: default employee_id ascending (numeric: 1, 2, 11 not string order)
    sort_by = request.args.get('sort_by', 'employee_id').strip().lower()
    order = request.args.get('order', 'asc').strip().lower()
    sort_columns = {
        'first_name': Employee.first_name,
        'last_name': Employee.last_name,
        'email': Employee.email,
        'job_title': Employee.job_title,
        'department_id': Employee.department_id,
        'date_joined': Employee.date_joined,
    }
    if sort_by == 'employee_id':
        # Extract numeric part (EMP001 -> 1, EMP0011 -> 11) for correct 1, 2, 11 order
        digits_only = func.regexp_replace(Employee.employee_id, r'[^0-9]', '', 'g')
        numeric_id = cast(func.coalesce(func.nullif(digits_only, ''), '0'), Integer)
        order_col = numeric_id
    else:
        order_col = sort_columns.get(sort_by, Employee.employee_id)
    if order == 'desc':
        q = q.order_by(order_col.desc())
    else:
        q = q.order_by(order_col.asc())
    employees = q.all()
    return jsonify([e.to_dict() for e in employees])

@employees_bp.route('/org-tree', methods=['GET'])
@jwt_required()
def org_tree():
    if get_jwt().get('role') != 'admin':
        return jsonify({'error': 'Admin only'}), 403
    # Root = no manager
    roots = Employee.query.filter_by(manager_id=None).all()
    if not roots:
        return jsonify([])
    if len(roots) == 1:
        return jsonify(roots[0].to_org_node())
    return jsonify([r.to_org_node() for r in roots])

@employees_bp.route('/<int:emp_id>', methods=['GET'])
@jwt_required()
def get_employee(emp_id):
    self_emp_id = get_employee_or_self()
    if self_emp_id is not None and self_emp_id != emp_id:
        return jsonify({'error': 'Forbidden'}), 403
    emp = Employee.query.get(emp_id)
    if not emp:
        return jsonify({'error': 'Employee not found'}), 404
    return jsonify(emp.to_dict())

@employees_bp.route('', methods=['POST'])
@admin_required()
def create_employee():
    data = request.get_json(silent=True) or {}
    if not data.get('first_name') or not data.get('last_name') or not data.get('email'):
        return jsonify({'error': 'first_name, last_name, email required'}), 400
    if Employee.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    eid = data.get('employee_id') or None
    if not eid:
        last = Employee.query.order_by(Employee.id.desc()).first()
        eid = f"EMP{((last.id if last else 0) + 1):04d}"
    if Employee.query.filter_by(employee_id=eid).first():
        return jsonify({'error': 'Employee ID already exists'}), 400
    # Coerce optional fields: empty string -> None, avoid invalid types for DB
    def _int_or_none(v):
        if v is None or v == '':
            return None
        try:
            return int(v)
        except (TypeError, ValueError):
            return None
    def _decimal_or_none(v):
        if v is None or v == '':
            return None
        try:
            return float(v)
        except (TypeError, ValueError):
            return None
    def _date_or_none(v):
        if not v:
            return None
        try:
            return datetime.strptime(str(v).strip()[:10], '%Y-%m-%d').date()
        except (TypeError, ValueError):
            return None
    dob = _date_or_none(data.get('date_of_birth'))
    dj = _date_or_none(data.get('date_joined')) or datetime.utcnow().date()
    emp = Employee(
        employee_id=eid,
        first_name=data['first_name'].strip(),
        last_name=data['last_name'].strip(),
        email=data['email'].strip(),
        phone=(data.get('phone') or '').strip() or None,
        gender=(data.get('gender') or '').strip() or None,
        date_of_birth=dob,
        address=(data.get('address') or '').strip() or None,
        job_title=(data.get('job_title') or '').strip() or None,
        department_id=_int_or_none(data.get('department_id')),
        manager_id=_int_or_none(data.get('manager_id')),
        salary=_decimal_or_none(data.get('salary')),
        date_joined=dj,
    )
    db.session.add(emp)
    db.session.commit()
    return jsonify(emp.to_dict()), 201

@employees_bp.route('/<int:emp_id>', methods=['PUT'])
@jwt_required()
def update_employee(emp_id):
    self_emp_id = get_employee_or_self()
    is_admin = get_jwt().get('role') == 'admin'
    if self_emp_id is not None and self_emp_id != emp_id and not is_admin:
        return jsonify({'error': 'Forbidden'}), 403
    emp = Employee.query.get(emp_id)
    if not emp:
        return jsonify({'error': 'Employee not found'}), 404
    data = request.get_json(silent=True) or {}
    def _parse_date(v):
        if not v or (isinstance(v, str) and not v.strip()):
            return None
        try:
            return datetime.strptime(str(v).strip()[:10], '%Y-%m-%d').date()
        except (TypeError, ValueError):
            return None
    # Employees can update limited fields; admin can update all
    allowed_employee = ['first_name', 'last_name', 'phone', 'address', 'date_of_birth']
    for key in ['first_name', 'last_name', 'email', 'phone', 'gender', 'date_of_birth', 'address', 'job_title', 'department_id', 'manager_id', 'salary', 'date_joined']:
        if key not in data:
            continue
        if not is_admin and key not in allowed_employee:
            continue
        if key == 'date_of_birth':
            emp.date_of_birth = _parse_date(data[key])
        elif key == 'date_joined':
            val = _parse_date(data[key])
            if val is not None:
                emp.date_joined = val
        elif key == 'email':
            other = Employee.query.filter_by(email=data['email']).first()
            if other and other.id != emp_id:
                return jsonify({'error': 'Email already exists'}), 400
            emp.email = data['email']
        elif key in ['department_id', 'manager_id']:
            setattr(emp, key, data[key] if data[key] not in (None, '', 0) else None)
        elif key == 'salary':
            val = data[key]
            setattr(emp, key, None if val in (None, '') else (float(val) if isinstance(val, (int, float)) else None))
        else:
            setattr(emp, key, data[key])
    db.session.commit()
    return jsonify(emp.to_dict())

@employees_bp.route('/<int:emp_id>', methods=['DELETE'])
@admin_required()
def delete_employee(emp_id):
    emp = Employee.query.get(emp_id)
    if not emp:
        return jsonify({'error': 'Employee not found'}), 404
    User.query.filter_by(employee_id=emp_id).delete()
    # Reassign subordinates' manager to emp's manager
    Employee.query.filter_by(manager_id=emp_id).update({'manager_id': emp.manager_id})
    db.session.delete(emp)
    db.session.commit()
    return jsonify({'message': 'Deleted'}), 200
