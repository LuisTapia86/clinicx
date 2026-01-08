#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Initialize database using Flask CLI
export FLASK_APP=run.py
flask init_db

# Create admin user
python << 'PYTHON_SCRIPT'
import os
os.environ['FLASK_ENV'] = 'production'

from app import create_app, db
from app.models import User

app = create_app('production')

with app.app_context():
    # Create admin user if not exists
    if User.query.count() == 0:
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
        print('Admin user created: username=admin, password=admin123')
    else:
        print('Admin user already exists')
PYTHON_SCRIPT
