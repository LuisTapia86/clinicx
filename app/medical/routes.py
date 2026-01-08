from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.medical import medical_bp
from app.models import MedicalRecord, Patient
from app import db
from datetime import datetime


@medical_bp.route('/patient/<int:patient_id>')
@login_required
def patient_records(patient_id):
    """View all medical records for a patient"""
    patient = Patient.query.get_or_404(patient_id)
    page = request.args.get('page', 1, type=int)

    records = MedicalRecord.query.filter_by(patient_id=patient_id).order_by(
        MedicalRecord.visit_date.desc()
    ).paginate(page=page, per_page=10, error_out=False)

    return render_template('medical/patient_records.html', patient=patient, records=records)


@medical_bp.route('/view/<int:record_id>')
@login_required
def view(record_id):
    """View a specific medical record"""
    record = MedicalRecord.query.get_or_404(record_id)
    return render_template('medical/view.html', record=record)


@medical_bp.route('/create/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def create(patient_id):
    """Create new medical record for a patient"""
    patient = Patient.query.get_or_404(patient_id)

    if request.method == 'POST':
        # Get form data
        visit_reason = request.form.get('visit_reason')
        diagnosis = request.form.get('diagnosis')

        if not visit_reason or not diagnosis:
            flash('Visit reason and diagnosis are required.', 'danger')
            return render_template('medical/create.html', patient=patient)

        # Create medical record
        record = MedicalRecord(
            patient_id=patient_id,
            visit_date=datetime.utcnow(),
            visit_reason=visit_reason,
            # Vital signs
            temperature=float(request.form.get('temperature')) if request.form.get('temperature') else None,
            blood_pressure_systolic=int(request.form.get('blood_pressure_systolic')) if request.form.get('blood_pressure_systolic') else None,
            blood_pressure_diastolic=int(request.form.get('blood_pressure_diastolic')) if request.form.get('blood_pressure_diastolic') else None,
            heart_rate=int(request.form.get('heart_rate')) if request.form.get('heart_rate') else None,
            respiratory_rate=int(request.form.get('respiratory_rate')) if request.form.get('respiratory_rate') else None,
            oxygen_saturation=float(request.form.get('oxygen_saturation')) if request.form.get('oxygen_saturation') else None,
            weight=float(request.form.get('weight')) if request.form.get('weight') else None,
            height=float(request.form.get('height')) if request.form.get('height') else None,
            # Medical information
            symptoms=request.form.get('symptoms'),
            diagnosis=diagnosis,
            treatment=request.form.get('treatment'),
            prescription=request.form.get('prescription'),
            lab_results=request.form.get('lab_results'),
            imaging_results=request.form.get('imaging_results'),
            # Follow-up
            follow_up_required=request.form.get('follow_up_required') == 'on',
            follow_up_date=datetime.strptime(request.form.get('follow_up_date'), '%Y-%m-%d').date() if request.form.get('follow_up_date') else None,
            follow_up_notes=request.form.get('follow_up_notes'),
            # Doctor notes
            doctor_notes=request.form.get('doctor_notes')
        )

        db.session.add(record)
        db.session.commit()

        flash('Medical record created successfully!', 'success')
        return redirect(url_for('medical.view', record_id=record.id))

    return render_template('medical/create.html', patient=patient)


@medical_bp.route('/edit/<int:record_id>', methods=['GET', 'POST'])
@login_required
def edit(record_id):
    """Edit a medical record"""
    record = MedicalRecord.query.get_or_404(record_id)

    if request.method == 'POST':
        # Update record
        record.visit_reason = request.form.get('visit_reason')
        record.diagnosis = request.form.get('diagnosis')
        record.temperature = float(request.form.get('temperature')) if request.form.get('temperature') else None
        record.blood_pressure_systolic = int(request.form.get('blood_pressure_systolic')) if request.form.get('blood_pressure_systolic') else None
        record.blood_pressure_diastolic = int(request.form.get('blood_pressure_diastolic')) if request.form.get('blood_pressure_diastolic') else None
        record.heart_rate = int(request.form.get('heart_rate')) if request.form.get('heart_rate') else None
        record.respiratory_rate = int(request.form.get('respiratory_rate')) if request.form.get('respiratory_rate') else None
        record.oxygen_saturation = float(request.form.get('oxygen_saturation')) if request.form.get('oxygen_saturation') else None
        record.weight = float(request.form.get('weight')) if request.form.get('weight') else None
        record.height = float(request.form.get('height')) if request.form.get('height') else None
        record.symptoms = request.form.get('symptoms')
        record.treatment = request.form.get('treatment')
        record.prescription = request.form.get('prescription')
        record.lab_results = request.form.get('lab_results')
        record.imaging_results = request.form.get('imaging_results')
        record.follow_up_required = request.form.get('follow_up_required') == 'on'
        record.follow_up_date = datetime.strptime(request.form.get('follow_up_date'), '%Y-%m-%d').date() if request.form.get('follow_up_date') else None
        record.follow_up_notes = request.form.get('follow_up_notes')
        record.doctor_notes = request.form.get('doctor_notes')

        db.session.commit()

        flash('Medical record updated successfully!', 'success')
        return redirect(url_for('medical.view', record_id=record.id))

    return render_template('medical/edit.html', record=record)


@medical_bp.route('/delete/<int:record_id>', methods=['POST'])
@login_required
def delete(record_id):
    """Delete a medical record"""
    if not current_user.is_admin() and not current_user.is_doctor():
        flash('Only administrators and doctors can delete medical records.', 'danger')
        return redirect(url_for('main.dashboard'))

    record = MedicalRecord.query.get_or_404(record_id)
    patient_id = record.patient_id

    db.session.delete(record)
    db.session.commit()

    flash('Medical record deleted successfully.', 'success')
    return redirect(url_for('medical.patient_records', patient_id=patient_id))
