from datetime import datetime
from app import db


class Patient(db.Model):
    """Patient model for storing patient information"""

    __tablename__ = 'patients'

    # Primary Key
    id = db.Column(db.Integer, primary_key=True)

    # Personal Information
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(20))  # 'male', 'female', 'other'
    blood_type = db.Column(db.String(5))  # 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'

    # Contact Information
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(256))
    city = db.Column(db.String(64))
    state = db.Column(db.String(64))
    zip_code = db.Column(db.String(10))
    country = db.Column(db.String(64))

    # Emergency Contact
    emergency_contact_name = db.Column(db.String(128))
    emergency_contact_phone = db.Column(db.String(20))
    emergency_contact_relationship = db.Column(db.String(64))

    # Medical Information
    insurance_provider = db.Column(db.String(128))
    insurance_number = db.Column(db.String(64))
    allergies = db.Column(db.Text)  # Comma-separated or JSON
    chronic_conditions = db.Column(db.Text)  # Comma-separated or JSON

    # Status
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Notes
    notes = db.Column(db.Text)  # General notes about the patient

    # Referral Information
    referred_by = db.Column(db.String(128))  # Name of person who referred this patient
    referral_source = db.Column(db.String(64))  # How they heard about the clinic: 'social_media', 'friend_family', 'doctor_referral', 'online_search', 'advertisement', 'walk_in', 'other'
    referral_notes = db.Column(db.Text)  # Additional notes about the referral

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    medical_records = db.relationship('MedicalRecord',
                                     backref='patient',
                                     lazy='dynamic',
                                     cascade='all, delete-orphan',
                                     order_by='MedicalRecord.visit_date.desc()')

    appointments = db.relationship('Appointment',
                                  backref='patient',
                                  lazy='dynamic',
                                  cascade='all, delete-orphan',
                                  order_by='Appointment.appointment_date.desc()')

    transactions = db.relationship('Transaction',
                                  backref='patient',
                                  lazy='dynamic',
                                  cascade='all, delete-orphan',
                                  order_by='Transaction.transaction_date.desc()')

    referrals = db.relationship('Referral',
                               backref='patient',
                               lazy='dynamic',
                               cascade='all, delete-orphan',
                               order_by='Referral.created_at.desc()')

    def __repr__(self):
        return f'<Patient {self.full_name}>'

    @property
    def full_name(self):
        """Get patient's full name"""
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self):
        """Calculate patient's age"""
        if self.date_of_birth:
            today = datetime.utcnow().date()
            age = today.year - self.date_of_birth.year
            if today.month < self.date_of_birth.month or \
               (today.month == self.date_of_birth.month and today.day < self.date_of_birth.day):
                age -= 1
            return age
        return None

    def get_latest_medical_record(self):
        """Get the most recent medical record"""
        return self.medical_records.first()

    def get_upcoming_appointments(self):
        """Get all upcoming appointments"""
        from app.models.appointment import Appointment
        return self.appointments.filter(
            Appointment.appointment_date >= datetime.utcnow(),
            Appointment.status != 'cancelled'
        ).order_by(Appointment.appointment_date.asc()).all()

    def get_total_debt(self):
        """Calculate total outstanding debt"""
        from app.models.transaction import Transaction
        total = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.patient_id == self.id,
            Transaction.transaction_type == 'income',
            Transaction.status == 'pending'
        ).scalar()
        return total or 0.0
