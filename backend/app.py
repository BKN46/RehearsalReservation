from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
import os

from models import db, init_db
from routes.auth import auth_bp
from routes.reservation import reservation_bp
from routes.admin import admin_bp
from routes.key_management import key_bp
from routes.equipment import equipment_bp

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rehearsal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Email verification feature flag
app.config['EMAIL_VERIFICATION_ENABLED'] = os.environ.get('EMAIL_VERIFICATION_ENABLED', 'false').lower() == 'true'

# Initialize extensions
CORS(app, resources={r"/api/*": {"origins": "*"}})
jwt = JWTManager(app)
db.init_app(app)

# Initialize email service if enabled
if app.config['EMAIL_VERIFICATION_ENABLED']:
    try:
        from email_service import init_mail
        init_mail(app)
        print("Email verification enabled")
    except Exception as e:
        print(f"Warning: Failed to initialize email service: {e}")
        app.config['EMAIL_VERIFICATION_ENABLED'] = False
else:
    print("Email verification disabled")

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(reservation_bp, url_prefix='/api/reservation')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(key_bp, url_prefix='/api/key')
app.register_blueprint(equipment_bp, url_prefix='/api/equipment')

# Initialize scheduled tasks
scheduler = None
try:
    from scheduled_tasks import init_scheduler
    with app.app_context():
        scheduler = init_scheduler(app)
except ImportError:
    print("Warning: APScheduler not installed. Scheduled tasks disabled.")
except Exception as e:
    print(f"Warning: Failed to initialize scheduler: {e}")

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True, host='0.0.0.0', port=8081)
