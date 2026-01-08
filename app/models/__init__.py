"""
Database models for ClinicX
All models are connected through foreign keys and relationships
"""

from app.models.user import User
from app.models.patient import Patient
from app.models.medical_record import MedicalRecord
from app.models.appointment import Appointment
from app.models.transaction import Transaction
from app.models.referral import Referral

__all__ = [
    'User',
    'Patient',
    'MedicalRecord',
    'Appointment',
    'Transaction',
    'Referral'
]
