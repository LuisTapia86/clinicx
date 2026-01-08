from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models import Patient, Appointment, Transaction, MedicalRecord
from datetime import datetime, timedelta
from app import db

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Landing page - redirect to dashboard if logged in, otherwise to login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard with statistics and recent activity"""

    # Get current date
    today = datetime.utcnow().date()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    # Statistics
    stats = {
        'total_patients': Patient.query.filter_by(is_active=True).count(),
        'appointments_today': Appointment.query.filter(
            db.func.date(Appointment.appointment_date) == today,
            Appointment.status.in_(['scheduled', 'confirmed', 'in_progress'])
        ).count(),
        'appointments_week': Appointment.query.filter(
            Appointment.appointment_date >= week_start,
            Appointment.status.in_(['scheduled', 'confirmed', 'in_progress'])
        ).count(),
        'pending_payments': Transaction.query.filter_by(
            transaction_type='income',
            status='pending'
        ).count(),
    }

    # Financial summary (this month)
    income_this_month = Transaction.get_total_income(
        start_date=month_start,
        status='completed'
    )
    expenses_this_month = Transaction.get_total_expenses(
        start_date=month_start,
        status='completed'
    )
    balance_this_month = income_this_month - expenses_this_month

    stats['income_month'] = income_this_month
    stats['expenses_month'] = expenses_this_month
    stats['balance_month'] = balance_this_month

    # Recent appointments (next 5)
    upcoming_appointments = Appointment.query.filter(
        Appointment.appointment_date >= datetime.utcnow(),
        Appointment.status.in_(['scheduled', 'confirmed'])
    ).order_by(Appointment.appointment_date.asc()).limit(5).all()

    # Today's appointments
    today_appointments = Appointment.query.filter(
        db.func.date(Appointment.appointment_date) == today,
        Appointment.status.in_(['scheduled', 'confirmed', 'in_progress'])
    ).order_by(Appointment.appointment_date.asc()).all()

    # Recent patients (last 5 registered)
    recent_patients = Patient.query.order_by(
        Patient.created_at.desc()
    ).limit(5).all()

    # Recent transactions (last 5)
    recent_transactions = Transaction.query.order_by(
        Transaction.transaction_date.desc()
    ).limit(5).all()

    return render_template('dashboard.html',
                         stats=stats,
                         upcoming_appointments=upcoming_appointments,
                         today_appointments=today_appointments,
                         recent_patients=recent_patients,
                         recent_transactions=recent_transactions)
