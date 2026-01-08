import os
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_babel import Babel
from config import config

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
babel = Babel()


def create_app(config_name='default'):
    """Application factory for creating Flask app instances"""

    # Create Flask app
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config[config_name])

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)

    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    # Babel locale selector function
    def get_locale():
        # Try to get locale from session or user settings
        # For now, use browser's language preference
        return request.accept_languages.best_match(app.config['BABEL_SUPPORTED_LOCALES']) or app.config['BABEL_DEFAULT_LOCALE']

    # Initialize Babel with locale selector
    babel.init_app(app, locale_selector=get_locale)

    # Create upload folder if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Register blueprints
    from app.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.patients import patients_bp
    app.register_blueprint(patients_bp, url_prefix='/patients')

    from app.medical import medical_bp
    app.register_blueprint(medical_bp, url_prefix='/medical')

    from app.appointments import appointments_bp
    app.register_blueprint(appointments_bp, url_prefix='/appointments')

    from app.finance import finance_bp
    app.register_blueprint(finance_bp, url_prefix='/finance')

    # Register main/index routes
    from app import routes
    app.register_blueprint(routes.main_bp)

    # Create database tables
    with app.app_context():
        db.create_all()

        # Create default admin user if no users exist
        from app.models import User
        if User.query.count() == 0:
            admin = User(
                username='admin',
                email='admin@clinicx.com',
                first_name='Admin',
                last_name='User',
                role='admin',
                phone='0000000000'
            )
            admin.set_password('admin123')  # Change in production!
            db.session.add(admin)
            db.session.commit()
            print("Default admin user created: username='admin', password='admin123'")

    return app
