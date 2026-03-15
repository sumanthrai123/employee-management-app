from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from models import db, Department

departments_bp = Blueprint('departments', __name__)

def admin_required():
    def decorator(fn):
        from functools import wraps
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            if get_jwt().get('role') != 'admin':
                return jsonify({'error': 'Admin only'}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator

@departments_bp.route('', methods=['GET'])
@jwt_required()
def list_departments():
    depts = Department.query.order_by(Department.name).all()
    return jsonify([d.to_dict() for d in depts])

@departments_bp.route('/<int:dept_id>', methods=['GET'])
@jwt_required()
def get_department(dept_id):
    d = Department.query.get(dept_id)
    if not d:
        return jsonify({'error': 'Department not found'}), 404
    return jsonify(d.to_dict())

@departments_bp.route('', methods=['POST'])
@admin_required()
def create_department():
    data = request.get_json(silent=True) or {}
    if not data.get('name'):
        return jsonify({'error': 'name required'}), 400
    if Department.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'Department name already exists'}), 400
    d = Department(name=data['name'], description=data.get('description'))
    db.session.add(d)
    db.session.commit()
    return jsonify(d.to_dict()), 201

@departments_bp.route('/<int:dept_id>', methods=['PUT'])
@admin_required()
def update_department(dept_id):
    d = Department.query.get(dept_id)
    if not d:
        return jsonify({'error': 'Department not found'}), 404
    data = request.get_json(silent=True) or {}
    if data.get('name'):
        other = Department.query.filter_by(name=data['name']).first()
        if other and other.id != dept_id:
            return jsonify({'error': 'Department name already exists'}), 400
        d.name = data['name']
    if 'description' in data:
        d.description = data['description']
    db.session.commit()
    return jsonify(d.to_dict())

@departments_bp.route('/<int:dept_id>', methods=['DELETE'])
@admin_required()
def delete_department(dept_id):
    d = Department.query.get(dept_id)
    if not d:
        return jsonify({'error': 'Department not found'}), 404
    if d.employees:
        return jsonify({'error': 'Cannot delete department with employees. Reassign them first.'}), 400
    db.session.delete(d)
    db.session.commit()
    return jsonify({'message': 'Deleted'}), 200
