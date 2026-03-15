from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from sqlalchemy import func
from datetime import datetime
from models import db, Employee, Department

reports_bp = Blueprint('reports', __name__)

def _join_month_expr():
    """PostgreSQL: group by month for joining trends."""
    return func.date_trunc('month', Employee.date_joined)

@reports_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    if get_jwt().get('role') != 'admin':
        return jsonify({'error': 'Admin only'}), 403
    department_id = request.args.get('department_id', type=int)
    gender = request.args.get('gender', '').strip()
    q = Employee.query
    if department_id:
        q = q.filter(Employee.department_id == department_id)
    if gender:
        q = q.filter(Employee.gender == gender)
    employees = q.all()

    # Department distribution (respect filters)
    dept_q = db.session.query(Department.name, func.count(Employee.id)).outerjoin(Employee).group_by(Department.id, Department.name)
    if department_id:
        dept_q = dept_q.filter(Department.id == department_id)
    if gender:
        dept_q = dept_q.filter(Employee.gender == gender)
    department_distribution = [{'name': n, 'count': c} for n, c in dept_q.all()]

    # Gender distribution (from filtered or all)
    gender_q = Employee.query
    if department_id:
        gender_q = gender_q.filter(Employee.department_id == department_id)
    gender_counts = gender_q.with_entities(Employee.gender, func.count(Employee.id)).group_by(Employee.gender).all()
    gender_distribution = [{'name': (g or 'Not specified'), 'count': c} for g, c in gender_counts]

    # Joining trends (by year-month) - SQLite and PostgreSQL compatible
    month_expr = _join_month_expr()
    join_q = db.session.query(
        month_expr.label('month'),
        func.count(Employee.id).label('count')
    ).filter(Employee.date_joined.isnot(None)).group_by(month_expr).order_by(month_expr)
    if department_id:
        join_q = join_q.filter(Employee.department_id == department_id)
    if gender:
        join_q = join_q.filter(Employee.gender == gender)
    rows = join_q.all()
    joining_trends = [{'month': (m.isoformat()[:7] if hasattr(m, 'isoformat') else str(m)) if m else None, 'count': c} for m, c in rows]

    # Salary distribution buckets
    salary_q = Employee.query.filter(Employee.salary.isnot(None), Employee.salary > 0)
    if department_id:
        salary_q = salary_q.filter(Employee.department_id == department_id)
    if gender:
        salary_q = salary_q.filter(Employee.gender == gender)
    salaries = [float(r[0]) for r in salary_q.with_entities(Employee.salary).all()]
    if salaries:
        step = (max(salaries) - min(salaries)) / 5 or 1
        low = min(salaries)
        buckets = [
            {'range': f'{int(low)}-{int(low+step)}', 'count': sum(1 for s in salaries if low <= s < low+step)},
            {'range': f'{int(low+step)}-{int(low+2*step)}', 'count': sum(1 for s in salaries if low+step <= s < low+2*step)},
            {'range': f'{int(low+2*step)}-{int(low+3*step)}', 'count': sum(1 for s in salaries if low+2*step <= s < low+3*step)},
            {'range': f'{int(low+3*step)}-{int(low+4*step)}', 'count': sum(1 for s in salaries if low+3*step <= s < low+4*step)},
            {'range': f'{int(low+4*step)}+', 'count': sum(1 for s in salaries if s >= low+4*step)},
        ]
    else:
        buckets = []

    return jsonify({
        'total_employees': len(employees),
        'department_distribution': department_distribution,
        'gender_distribution': gender_distribution,
        'joining_trends': joining_trends,
        'salary_distribution': buckets,
    })
