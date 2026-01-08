from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager


class User(UserMixin, db.Model):
    """User model for system authentication and role-based access"""

    __tablename__ = 'users'

    # Primary Key
    id = db.Column(db.Integer, primary_key=True)

    # Authentication
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)

    # User Information
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    phone = db.Column(db.String(20))

    # Role: 'admin', 'doctor', 'receptionist'
    role = db.Column(db.String(20), nullable=False, default='receptionist')

    # Status
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime)

    # Relationships
    appointments_created = db.relationship('Appointment',
                                          foreign_keys='Appointment.created_by_id',
                                          backref='created_by',
                                          lazy='dynamic')

    transactions_created = db.relationship('Transaction',
                                          foreign_keys='Transaction.created_by_id',
                                          backref='created_by',
                                          lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'

    def set_password(self, password):
        """Hash and set user password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self):
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}"

    def is_admin(self):
        """Check if user is admin"""
        return self.role == 'admin'

    def is_doctor(self):
        """Check if user is doctor"""
        return self.role == 'doctor'

    def is_receptionist(self):
        """Check if user is receptionist"""
        return self.role == 'receptionist'

    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
        db.session.commit()


@login_manager.user_loader
def load_user(user_id):
    """Flask-Login user loader"""
    return User.query.get(int(user_id))
