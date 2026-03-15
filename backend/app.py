from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from models import db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    CORS(app, origins=[
        'http://localhost:3000', 'http://localhost:5173', 'http://localhost:5174', 'http://localhost:5175',
        'http://127.0.0.1:3000', 'http://127.0.0.1:5173', 'http://127.0.0.1:5174', 'http://127.0.0.1:5175',
    ], supports_credentials=True, allow_headers=['Content-Type', 'Authorization'])
    db.init_app(app)
    jwt = JWTManager(app)

    # Return 401 (not 422) for invalid JWT so frontend can treat all auth failures the same
    @jwt.invalid_token_loader
    def invalid_token_callback(error_string):
        return jsonify({'error': 'Invalid or expired token. Please log in again.', 'msg': error_string}), 401

    from routes.auth import auth_bp
    from routes.employees import employees_bp
    from routes.departments import departments_bp
    from routes.reports import reports_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(employees_bp, url_prefix='/api/employees')
    app.register_blueprint(departments_bp, url_prefix='/api/departments')
    app.register_blueprint(reports_bp, url_prefix='/api/reports')

    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
