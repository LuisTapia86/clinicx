from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.appointments import appointments_bp
from app.models import Appointment, Patient
from app import db
from datetime import datetime, timedelta


@appointments_bp.route('/')
@login_required
def index():
    """List all appointments"""
    page = request.args.get('page', 1, type=int)
    filter_status = request.args.get('status', 'all', type=str)
    filter_date = request.args.get('date', '', type=str)

    query = Appointment.query

    # Filter by status
    if filter_status != 'all':
        query = query.filter_by(status=filter_status)

    # Filter by date
    if filter_date:
        date_obj = datetime.strptime(filter_date, '%Y-%m-%d').date()
        query = query.filter(db.func.date(Appointment.appointment_date) == date_obj)

    appointments = query.order_by(Appointment.appointment_date.desc()).paginate(
        page=page,
        per_page=10,
        error_out=False
    )

    return render_template('appointments/index.html',
                         appointments=appointments,
                         filter_status=filter_status,
                         filter_date=filter_date)


@appointments_bp.route('/calendar')
@login_required
def calendar():
    """Calendar view of appointments"""
    return render_template('appointments/calendar.html')


@appointments_bp.route('/api/appointments')
@login_required
def api_appointments():
    """API endpoint for calendar appointments"""
    start = request.args.get('start')
    end = request.args.get('end')

    query = Appointment.query

    if start:
        start_date = datetime.fromisoformat(start.replace('Z', '+00:00'))
        query = query.filter(Appointment.appointment_date >= start_date)

    if end:
        end_date = datetime.fromisoformat(end.replace('Z', '+00:00'))
        query = query.filter(Appointment.appointment_date <= end_date)

    appointments = query.all()

    events = []
    for apt in appointments:
        color = {
            'scheduled': '#6c757d',
            'confirmed': '#007bff',
            'in_progress': '#ffc107',
            'completed': '#28a745',
            'cancelled': '#dc3545',
            'no_show': '#fd7e14'
        }.get(apt.status, '#6c757d')

        events.append({
            'id': apt.id,
            'title': f'{apt.patient.full_name} - {apt.reason}',
            'start': apt.appointment_date.isoformat(),
            'end': apt.end_time.isoformat(),
            'color': color,
            'extendedProps': {
                'patient_id': apt.patient_id,
                'status': apt.status,
                'reason': apt.reason
            }
        })

    return jsonify(events)


@appointments_bp.route('/view/<int:appointment_id>')
@login_required
def view(appointment_id):
    """View appointment details"""
    appointment = Appointment.query.get_or_404(appointment_id)
    return render_template('appointments/view.html', appointment=appointment)


@appointments_bp.route('/create', methods=['GET', 'POST'])
@appointments_bp.route('/create/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def create(patient_id=None):
    """Create new appointment"""
    patients = Patient.query.filter_by(is_active=True).order_by(Patient.first_name).all()

    if request.method == 'POST':
        # Get form data
        patient_id_form = request.form.get('patient_id')
        appointment_date = request.form.get('appointment_date')
        appointment_time = request.form.get('appointment_time')
        duration_str = request.form.get('duration_minutes', '30')
        reason = request.form.get('reason')
        appointment_type = request.form.get('appointment_type')

        # Validate patient_id
        if not patient_id_form or patient_id_form == '':
            flash('Please select a patient.', 'danger')
            return render_template('appointments/create.html', patients=patients, selected_patient_id=None)

        try:
            patient_id = int(patient_id_form)
            duration = int(duration_str)
        except ValueError:
            flash('Invalid patient or duration value.', 'danger')
            return render_template('appointments/create.html', patients=patients, selected_patient_id=None)

        if not all([appointment_date, appointment_time, reason]):
            flash('Please fill in all required fields.', 'danger')
            return render_template('appointments/create.html', patients=patients, selected_patient_id=patient_id)

        # Combine date and time
        datetime_str = f"{appointment_date} {appointment_time}"
        appointment_datetime = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')

        # Check for conflicts
        conflicts = Appointment.get_schedule_conflicts(appointment_datetime, duration)
        if conflicts:
            flash(f'Schedule conflict detected! There are {len(conflicts)} overlapping appointments.', 'warning')

        # Create appointment
        appointment = Appointment(
            patient_id=patient_id,
            created_by_id=current_user.id,
            appointment_date=appointment_datetime,
            duration_minutes=duration,
            appointment_type=appointment_type,
            reason=reason,
            cost=float(request.form.get('cost', 0)),
            notes=request.form.get('notes')
        )

        db.session.add(appointment)
        db.session.commit()

        flash('Appointment created successfully!', 'success')
        return redirect(url_for('appointments.view', appointment_id=appointment.id))

    return render_template('appointments/create.html',
                         patients=patients,
                         selected_patient_id=patient_id)


@appointments_bp.route('/edit/<int:appointment_id>', methods=['GET', 'POST'])
@login_required
def edit(appointment_id):
    """Edit appointment"""
    appointment = Appointment.query.get_or_404(appointment_id)
    patients = Patient.query.filter_by(is_active=True).order_by(Patient.first_name).all()

    if request.method == 'POST':
        # Update appointment
        patient_id_form = request.form.get('patient_id')
        if patient_id_form:
            try:
                appointment.patient_id = int(patient_id_form)
            except ValueError:
                flash('Invalid patient selected.', 'danger')
                return render_template('appointments/edit.html', appointment=appointment, patients=patients)

        appointment_date = request.form.get('appointment_date')
        appointment_time = request.form.get('appointment_time')
        datetime_str = f"{appointment_date} {appointment_time}"
        appointment.appointment_date = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')

        duration_str = request.form.get('duration_minutes', '30')
        try:
            appointment.duration_minutes = int(duration_str)
        except ValueError:
            appointment.duration_minutes = 30
        appointment.appointment_type = request.form.get('appointment_type')
        appointment.reason = request.form.get('reason')
        appointment.status = request.form.get('status')
        appointment.cost = float(request.form.get('cost', 0))
        appointment.notes = request.form.get('notes')

        db.session.commit()

        flash('Appointment updated successfully!', 'success')
        return redirect(url_for('appointments.view', appointment_id=appointment.id))

    return render_template('appointments/edit.html', appointment=appointment, patients=patients)


@appointments_bp.route('/cancel/<int:appointment_id>', methods=['POST'])
@login_required
def cancel(appointment_id):
    """Cancel appointment"""
    appointment = Appointment.query.get_or_404(appointment_id)
    reason = request.form.get('cancellation_reason', 'No reason provided')

    if appointment.cancel(reason):
        flash('Appointment cancelled successfully.', 'success')
    else:
        flash('Could not cancel this appointment.', 'danger')

    return redirect(url_for('appointments.view', appointment_id=appointment_id))


@appointments_bp.route('/complete/<int:appointment_id>', methods=['POST'])
@login_required
def complete(appointment_id):
    """Mark appointment as completed"""
    appointment = Appointment.query.get_or_404(appointment_id)

    if appointment.complete():
        flash('Appointment marked as completed.', 'success')
    else:
        flash('Could not complete this appointment.', 'danger')

    return redirect(url_for('appointments.view', appointment_id=appointment_id))


@appointments_bp.route('/confirm/<int:appointment_id>', methods=['POST'])
@login_required
def confirm(appointment_id):
    """Confirm appointment"""
    appointment = Appointment.query.get_or_404(appointment_id)

    if appointment.confirm():
        flash('Appointment confirmed.', 'success')
    else:
        flash('Could not confirm this appointment.', 'danger')

    return redirect(url_for('appointments.view', appointment_id=appointment_id))
