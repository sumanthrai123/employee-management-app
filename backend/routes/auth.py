from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt
from models import db, User, Employee

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json(silent=True) or {}
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    # Registration creates employee + user; employee_id can be set by admin or auto-generated
    emp_id = data.get('employee_id')
    if not emp_id:
        last = Employee.query.order_by(Employee.id.desc()).first()
        emp_id = f"EMP{((last.id if last else 0) + 1):04d}"
    def _int_or_none(v):
        if v is None or v == '':
            return None
        try:
            return int(v)
        except (TypeError, ValueError):
            return None
    emp = Employee(
        employee_id=emp_id,
        first_name=(data.get('first_name') or '').strip(),
        last_name=(data.get('last_name') or '').strip(),
        email=data['email'].strip(),
        phone=(data.get('phone') or '').strip() or None,
        gender=(data.get('gender') or '').strip() or None,
        job_title=(data.get('job_title') or '').strip() or None,
        department_id=_int_or_none(data.get('department_id')),
        manager_id=_int_or_none(data.get('manager_id')),
    )
    db.session.add(emp)
    db.session.flush()
    user = User(email=data['email'], role='employee', employee_id=emp.id)
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    token = create_access_token(identity=str(user.id), additional_claims={'role': user.role, 'employee_id': emp.id})
    return jsonify({'token': token, 'user': user.to_dict(), 'employee': emp.to_dict()}), 201

@auth_bp.route('/login/employee', methods=['POST'])
def login_employee():
    data = request.get_json(silent=True) or {}
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400
    user = User.query.filter_by(email=data['email'], role='employee').first()
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    emp = Employee.query.get(user.employee_id)
    token = create_access_token(identity=str(user.id), additional_claims={'role': user.role, 'employee_id': user.employee_id})
    return jsonify({'token': token, 'user': user.to_dict(), 'employee': emp.to_dict() if emp else None})

@auth_bp.route('/login/admin', methods=['POST'])
def login_admin():
    data = request.get_json(silent=True) or {}
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400
    user = User.query.filter_by(email=data['email'], role='admin').first()
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    # Use string identity to avoid JSON number issues; claims for role
    token = create_access_token(identity=str(user.id), additional_claims={'role': user.role})
    return jsonify({'token': token, 'user': user.to_dict()})

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    uid = get_jwt_identity()
    try:
        uid = int(uid) if uid is not None else None
    except (TypeError, ValueError):
        uid = None
    if uid is None:
        return jsonify({'error': 'Invalid token identity'}), 401
    user = User.query.get(uid)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    out = user.to_dict()
    if user.role == 'employee' and user.employee_id:
        emp = Employee.query.get(user.employee_id)
        out['employee'] = emp.to_dict() if emp else None
    return jsonify(out)
