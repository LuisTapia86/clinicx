#!/usr/bin/env bash
# exit on error
set -o errexit

echo "==> Upgrading pip..."
pip install --upgrade pip

echo "==> Installing dependencies..."
pip install -r requirements.txt

echo "==> Initializing database and creating admin user..."
python << 'PYTHON_SCRIPT'
import os

# Force production environment
os.environ['FLASK_ENV'] = 'production'

from app import create_app, db
from app.models import User

print("Creating Flask app in production mode...")
app = create_app('production')

with app.app_context():
    print(f"Database URL: {app.config['SQLALCHEMY_DATABASE_URI'][:50]}...")

    print("Creating all database tables...")
    db.create_all()
    print("Database tables created successfully!")

    # Create admin user if not exists
    user_count = User.query.count()
    print(f"Current user count: {user_count}")

    if user_count == 0:
        print("Creating admin user...")
        admin = User(
            username='admin',
            email='admin@clinicx.com',
            first_name='Admin',
            last_name='User',
            role='admin',
            phone='0000000000'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print('✓ Admin user created successfully!')
        print('  Username: admin')
        print('  Password: admin123')
    else:
        print('✓ Admin user already exists')

print("==> Build completed successfully!")
PYTHON_SCRIPT
