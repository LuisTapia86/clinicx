"""
Referral Model
Handles people that patients want to refer to the clinic
"""
from datetime import datetime
from app import db


class Referral(db.Model):
    """
    Model to store referrals made by patients
    When a patient wants to refer a family member, friend, etc.
    """
    __tablename__ = 'referrals'

    # Primary Key
    id = db.Column(db.Integer, primary_key=True)

    # Foreign Keys
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False)

    # Referred Person Information
    referred_name = db.Column(db.String(128), nullable=False)  # Name of person being referred
    referred_phone = db.Column(db.String(20), nullable=False)  # Phone number to contact them
    referred_email = db.Column(db.String(120))  # Optional email
    relationship = db.Column(db.String(64))  # Relationship to patient: 'family', 'friend', 'coworker', 'neighbor', 'other'

    # Referral Details
    notes = db.Column(db.Text)  # Additional notes about the referral
    status = db.Column(db.String(20), default='pending', nullable=False)  # 'pending', 'contacted', 'scheduled', 'converted', 'declined'

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    contacted_at = db.Column(db.DateTime)  # When we contacted them

    def __repr__(self):
        return f'<Referral {self.referred_name} by Patient #{self.patient_id}>'

    @property
    def status_badge_class(self):
        """Return Bootstrap badge class based on status"""
        status_classes = {
            'pending': 'bg-warning',
            'contacted': 'bg-info',
            'scheduled': 'bg-primary',
            'converted': 'bg-success',
            'declined': 'bg-secondary'
        }
        return status_classes.get(self.status, 'bg-secondary')

    @property
    def relationship_display(self):
        """Return friendly display name for relationship"""
        relationships = {
            'family': 'Family Member',
            'friend': 'Friend',
            'coworker': 'Coworker',
            'neighbor': 'Neighbor',
            'other': 'Other'
        }
        return relationships.get(self.relationship, self.relationship or 'Not specified')
