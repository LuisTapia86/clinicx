from datetime import datetime, timedelta
from app import db


class Appointment(db.Model):
    """Appointment model for scheduling patient visits"""

    __tablename__ = 'appointments'

    # Primary Key
    id = db.Column(db.Integer, primary_key=True)

    # Foreign Keys
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False, index=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    # Appointment Information
    appointment_date = db.Column(db.DateTime, nullable=False, index=True)
    duration_minutes = db.Column(db.Integer, default=30, nullable=False)  # Default 30 minutes
    appointment_type = db.Column(db.String(64))  # 'consultation', 'follow_up', 'emergency', 'surgery', etc.
    reason = db.Column(db.String(256), nullable=False)

    # Status: 'scheduled', 'confirmed', 'in_progress', 'completed', 'cancelled', 'no_show'
    status = db.Column(db.String(20), default='scheduled', nullable=False, index=True)

    # Payment
    cost = db.Column(db.Float, default=0.0)
    paid = db.Column(db.Boolean, default=False, nullable=False)

    # Notes
    notes = db.Column(db.Text)  # Additional notes for the appointment
    cancellation_reason = db.Column(db.Text)  # Reason if cancelled

    # Reminders
    reminder_sent = db.Column(db.Boolean, default=False)
    reminder_sent_at = db.Column(db.DateTime)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = db.Column(db.DateTime)
    cancelled_at = db.Column(db.DateTime)

    def __repr__(self):
        return f'<Appointment {self.id} Patient:{self.patient_id} Date:{self.appointment_date.strftime("%Y-%m-%d %H:%M")}>'

    @property
    def end_time(self):
        """Calculate appointment end time"""
        return self.appointment_date + timedelta(minutes=self.duration_minutes)

    def is_past(self):
        """Check if appointment is in the past"""
        return self.appointment_date < datetime.utcnow()

    def is_today(self):
        """Check if appointment is today"""
        today = datetime.utcnow().date()
        return self.appointment_date.date() == today

    def is_upcoming(self):
        """Check if appointment is upcoming"""
        return self.appointment_date > datetime.utcnow() and self.status not in ['cancelled', 'completed']

    def can_cancel(self):
        """Check if appointment can be cancelled"""
        return self.status in ['scheduled', 'confirmed'] and not self.is_past()

    def can_complete(self):
        """Check if appointment can be marked as completed"""
        return self.status in ['scheduled', 'confirmed', 'in_progress']

    def cancel(self, reason=None):
        """Cancel the appointment"""
        if self.can_cancel():
            self.status = 'cancelled'
            self.cancelled_at = datetime.utcnow()
            if reason:
                self.cancellation_reason = reason
            db.session.commit()
            return True
        return False

    def complete(self):
        """Mark appointment as completed"""
        if self.can_complete():
            self.status = 'completed'
            self.completed_at = datetime.utcnow()
            db.session.commit()
            return True
        return False

    def confirm(self):
        """Confirm the appointment"""
        if self.status == 'scheduled':
            self.status = 'confirmed'
            db.session.commit()
            return True
        return False

    def mark_no_show(self):
        """Mark patient as no-show"""
        if self.is_past() and self.status in ['scheduled', 'confirmed']:
            self.status = 'no_show'
            db.session.commit()
            return True
        return False

    @staticmethod
    def get_schedule_conflicts(appointment_date, duration_minutes, exclude_id=None):
        """Check for scheduling conflicts"""
        end_time = appointment_date + timedelta(minutes=duration_minutes)

        query = Appointment.query.filter(
            Appointment.status.in_(['scheduled', 'confirmed', 'in_progress']),
            Appointment.appointment_date < end_time,
            db.func.datetime(Appointment.appointment_date,
                           '+' + db.cast(Appointment.duration_minutes, db.String) + ' minutes') > appointment_date
        )

        if exclude_id:
            query = query.filter(Appointment.id != exclude_id)

        return query.all()

    def time_until_appointment(self):
        """Get time remaining until appointment"""
        if self.is_past():
            return None
        delta = self.appointment_date - datetime.utcnow()
        return delta
