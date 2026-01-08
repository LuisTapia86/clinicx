from datetime import datetime
from app import db


class MedicalRecord(db.Model):
    """Medical Record model for storing patient medical history"""

    __tablename__ = 'medical_records'

    # Primary Key
    id = db.Column(db.Integer, primary_key=True)

    # Foreign Keys
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False, index=True)

    # Visit Information
    visit_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    visit_reason = db.Column(db.String(256), nullable=False)

    # Vital Signs
    temperature = db.Column(db.Float)  # Celsius
    blood_pressure_systolic = db.Column(db.Integer)  # mmHg
    blood_pressure_diastolic = db.Column(db.Integer)  # mmHg
    heart_rate = db.Column(db.Integer)  # BPM
    respiratory_rate = db.Column(db.Integer)  # Breaths per minute
    oxygen_saturation = db.Column(db.Float)  # Percentage
    weight = db.Column(db.Float)  # Kilograms
    height = db.Column(db.Float)  # Centimeters

    # Medical Information
    symptoms = db.Column(db.Text)
    diagnosis = db.Column(db.Text, nullable=False)
    treatment = db.Column(db.Text)
    prescription = db.Column(db.Text)  # Medications prescribed
    lab_results = db.Column(db.Text)  # Laboratory test results
    imaging_results = db.Column(db.Text)  # X-ray, MRI, CT scan results

    # Follow-up
    follow_up_required = db.Column(db.Boolean, default=False)
    follow_up_date = db.Column(db.Date)
    follow_up_notes = db.Column(db.Text)

    # Files
    attachments = db.Column(db.Text)  # JSON array of file paths

    # Doctor Notes
    doctor_notes = db.Column(db.Text)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<MedicalRecord Patient:{self.patient_id} Date:{self.visit_date.strftime("%Y-%m-%d")}>'

    @property
    def blood_pressure(self):
        """Get blood pressure as formatted string"""
        if self.blood_pressure_systolic and self.blood_pressure_diastolic:
            return f"{self.blood_pressure_systolic}/{self.blood_pressure_diastolic}"
        return None

    @property
    def bmi(self):
        """Calculate BMI (Body Mass Index)"""
        if self.weight and self.height:
            height_m = self.height / 100  # Convert cm to meters
            bmi = self.weight / (height_m ** 2)
            return round(bmi, 2)
        return None

    def get_bmi_category(self):
        """Get BMI category"""
        bmi = self.bmi
        if bmi is None:
            return None
        if bmi < 18.5:
            return 'Underweight'
        elif 18.5 <= bmi < 25:
            return 'Normal'
        elif 25 <= bmi < 30:
            return 'Overweight'
        else:
            return 'Obese'

    def has_abnormal_vitals(self):
        """Check if any vital signs are abnormal"""
        abnormal = False

        # Temperature (normal: 36.5-37.5°C)
        if self.temperature and (self.temperature < 36.0 or self.temperature > 37.5):
            abnormal = True

        # Blood Pressure (normal systolic: 90-120, diastolic: 60-80)
        if self.blood_pressure_systolic and (self.blood_pressure_systolic < 90 or self.blood_pressure_systolic > 140):
            abnormal = True
        if self.blood_pressure_diastolic and (self.blood_pressure_diastolic < 60 or self.blood_pressure_diastolic > 90):
            abnormal = True

        # Heart Rate (normal: 60-100 BPM)
        if self.heart_rate and (self.heart_rate < 60 or self.heart_rate > 100):
            abnormal = True

        # Oxygen Saturation (normal: >95%)
        if self.oxygen_saturation and self.oxygen_saturation < 95:
            abnormal = True

        return abnormal
