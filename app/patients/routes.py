from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.patients import patients_bp
from app.models import Patient, Referral
from app import db
from datetime import datetime


@patients_bp.route('/')
@login_required
def index():
    """List all patients"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)

    query = Patient.query.filter_by(is_active=True)

    if search:
        query = query.filter(
            db.or_(
                Patient.first_name.ilike(f'%{search}%'),
                Patient.last_name.ilike(f'%{search}%'),
                Patient.email.ilike(f'%{search}%'),
                Patient.phone.ilike(f'%{search}%')
            )
        )

    patients = query.order_by(Patient.created_at.desc()).paginate(
        page=page,
        per_page=10,
        error_out=False
    )

    return render_template('patients/index.html', patients=patients, search=search)


@patients_bp.route('/view/<int:patient_id>')
@login_required
def view(patient_id):
    """View patient details"""
    patient = Patient.query.get_or_404(patient_id)
    return render_template('patients/view.html', patient=patient)


@patients_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create new patient"""
    if request.method == 'POST':
        # Get form data
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        date_of_birth = request.form.get('date_of_birth')
        gender = request.form.get('gender')
        phone = request.form.get('phone')
        email = request.form.get('email')

        # Validation
        if not first_name or not last_name or not date_of_birth or not phone:
            flash('Please fill in all required fields.', 'danger')
            return render_template('patients/create.html')

        # Create patient
        patient = Patient(
            first_name=first_name,
            last_name=last_name,
            date_of_birth=datetime.strptime(date_of_birth, '%Y-%m-%d').date(),
            gender=gender,
            phone=phone,
            email=email or None,
            blood_type=request.form.get('blood_type'),
            address=request.form.get('address'),
            city=request.form.get('city'),
            state=request.form.get('state'),
            zip_code=request.form.get('zip_code'),
            country=request.form.get('country'),
            emergency_contact_name=request.form.get('emergency_contact_name'),
            emergency_contact_phone=request.form.get('emergency_contact_phone'),
            emergency_contact_relationship=request.form.get('emergency_contact_relationship'),
            insurance_provider=request.form.get('insurance_provider'),
            insurance_number=request.form.get('insurance_number'),
            allergies=request.form.get('allergies'),
            chronic_conditions=request.form.get('chronic_conditions'),
            notes=request.form.get('notes'),
            referred_by=request.form.get('referred_by'),
            referral_source=request.form.get('referral_source'),
            referral_notes=request.form.get('referral_notes')
        )

        db.session.add(patient)
        db.session.commit()

        flash(f'Patient {patient.full_name} created successfully!', 'success')
        return redirect(url_for('patients.view', patient_id=patient.id))

    return render_template('patients/create.html')


@patients_bp.route('/edit/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def edit(patient_id):
    """Edit patient information"""
    patient = Patient.query.get_or_404(patient_id)

    if request.method == 'POST':
        # Update patient data
        patient.first_name = request.form.get('first_name')
        patient.last_name = request.form.get('last_name')
        patient.date_of_birth = datetime.strptime(request.form.get('date_of_birth'), '%Y-%m-%d').date()
        patient.gender = request.form.get('gender')
        patient.phone = request.form.get('phone')
        patient.email = request.form.get('email') or None
        patient.blood_type = request.form.get('blood_type')
        patient.address = request.form.get('address')
        patient.city = request.form.get('city')
        patient.state = request.form.get('state')
        patient.zip_code = request.form.get('zip_code')
        patient.country = request.form.get('country')
        patient.emergency_contact_name = request.form.get('emergency_contact_name')
        patient.emergency_contact_phone = request.form.get('emergency_contact_phone')
        patient.emergency_contact_relationship = request.form.get('emergency_contact_relationship')
        patient.insurance_provider = request.form.get('insurance_provider')
        patient.insurance_number = request.form.get('insurance_number')
        patient.allergies = request.form.get('allergies')
        patient.chronic_conditions = request.form.get('chronic_conditions')
        patient.notes = request.form.get('notes')
        patient.referred_by = request.form.get('referred_by')
        patient.referral_source = request.form.get('referral_source')
        patient.referral_notes = request.form.get('referral_notes')

        db.session.commit()

        flash(f'Patient {patient.full_name} updated successfully!', 'success')
        return redirect(url_for('patients.view', patient_id=patient.id))

    return render_template('patients/edit.html', patient=patient)


@patients_bp.route('/delete/<int:patient_id>', methods=['POST'])
@login_required
def delete(patient_id):
    """Soft delete patient (mark as inactive)"""
    if not current_user.is_admin():
        flash('Only administrators can delete patients.', 'danger')
        return redirect(url_for('patients.index'))

    patient = Patient.query.get_or_404(patient_id)
    patient.is_active = False
    db.session.commit()

    flash(f'Patient {patient.full_name} has been deactivated.', 'success')
    return redirect(url_for('patients.index'))


# ============================================================================
# REFERRAL ROUTES - For patients who want to refer others
# ============================================================================

@patients_bp.route('/<int:patient_id>/referrals/add', methods=['POST'])
@login_required
def add_referral(patient_id):
    """Add a new referral from a patient"""
    patient = Patient.query.get_or_404(patient_id)

    # Get form data
    referred_name = request.form.get('referred_name', '').strip()
    referred_phone = request.form.get('referred_phone', '').strip()
    referred_email = request.form.get('referred_email', '').strip()
    relationship = request.form.get('relationship', '').strip()
    notes = request.form.get('notes', '').strip()

    # Validate required fields
    if not referred_name or not referred_phone:
        flash('Name and phone number are required for referrals.', 'danger')
        return redirect(url_for('patients.view', patient_id=patient_id))

    # Create new referral
    referral = Referral(
        patient_id=patient_id,
        referred_name=referred_name,
        referred_phone=referred_phone,
        referred_email=referred_email if referred_email else None,
        relationship=relationship if relationship else None,
        notes=notes if notes else None,
        status='pending'
    )

    db.session.add(referral)
    db.session.commit()

    flash(f'Referral for {referred_name} has been added successfully!', 'success')
    return redirect(url_for('patients.view', patient_id=patient_id))


@patients_bp.route('/<int:patient_id>/referrals/<int:referral_id>/update-status', methods=['POST'])
@login_required
def update_referral_status(patient_id, referral_id):
    """Update referral status"""
    referral = Referral.query.get_or_404(referral_id)

    # Verify the referral belongs to this patient
    if referral.patient_id != patient_id:
        flash('Invalid referral.', 'danger')
        return redirect(url_for('patients.view', patient_id=patient_id))

    # Get new status
    new_status = request.form.get('status')
    valid_statuses = ['pending', 'contacted', 'scheduled', 'converted', 'declined']

    if new_status not in valid_statuses:
        flash('Invalid status.', 'danger')
        return redirect(url_for('patients.view', patient_id=patient_id))

    referral.status = new_status

    # Update contacted_at timestamp if status is changing to contacted
    if new_status == 'contacted' and not referral.contacted_at:
        referral.contacted_at = datetime.utcnow()

    db.session.commit()

    flash(f'Referral status updated to {new_status}.', 'success')
    return redirect(url_for('patients.view', patient_id=patient_id))


@patients_bp.route('/<int:patient_id>/referrals/<int:referral_id>/delete', methods=['POST'])
@login_required
def delete_referral(patient_id, referral_id):
    """Delete a referral"""
    referral = Referral.query.get_or_404(referral_id)

    # Verify the referral belongs to this patient
    if referral.patient_id != patient_id:
        flash('Invalid referral.', 'danger')
        return redirect(url_for('patients.view', patient_id=patient_id))

    referred_name = referral.referred_name
    db.session.delete(referral)
    db.session.commit()

    flash(f'Referral for {referred_name} has been deleted.', 'info')
    return redirect(url_for('patients.view', patient_id=patient_id))
