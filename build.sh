#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Initialize database and create admin user
python -c "
from app import create_app, db
from app.models import User

app = create_app('production')

with app.app_context():
    # Create all tables
    db.create_all()
    print('Database tables created successfully!')

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
"
