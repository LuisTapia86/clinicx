from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.finance import finance_bp
from app.models import Transaction, Patient, Appointment
from app import db
from datetime import datetime, timedelta


@finance_bp.route('/')
@login_required
def index():
    """Financial dashboard"""
    # Date filters
    filter_type = request.args.get('type', 'all', type=str)
    period = request.args.get('period', 'month', type=str)

    # Calculate date range
    today = datetime.utcnow()
    if period == 'today':
        start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = today
    elif period == 'week':
        start_date = today - timedelta(days=today.weekday())
        end_date = today
    elif period == 'month':
        start_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = today
    elif period == 'year':
        start_date = today.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = today
    else:
        start_date = None
        end_date = None

    # Calculate totals
    total_income = Transaction.get_total_income(start_date, end_date)
    total_expenses = Transaction.get_total_expenses(start_date, end_date)
    balance = total_income - total_expenses

    # Pending payments
    pending_income = Transaction.get_total_income(start_date, end_date, status='pending')

    # Recent transactions
    query = Transaction.query
    if filter_type != 'all':
        query = query.filter_by(transaction_type=filter_type)
    if start_date:
        query = query.filter(Transaction.transaction_date >= start_date)
    if end_date:
        query = query.filter(Transaction.transaction_date <= end_date)

    recent_transactions = query.order_by(
        Transaction.transaction_date.desc()
    ).limit(10).all()

    return render_template('finance/index.html',
                         total_income=total_income,
                         total_expenses=total_expenses,
                         balance=balance,
                         pending_income=pending_income,
                         recent_transactions=recent_transactions,
                         filter_type=filter_type,
                         period=period)


@finance_bp.route('/transactions')
@login_required
def transactions():
    """List all transactions"""
    page = request.args.get('page', 1, type=int)
    filter_type = request.args.get('type', 'all', type=str)
    filter_status = request.args.get('status', 'all', type=str)
    filter_category = request.args.get('category', 'all', type=str)

    query = Transaction.query

    if filter_type != 'all':
        query = query.filter_by(transaction_type=filter_type)
    if filter_status != 'all':
        query = query.filter_by(status=filter_status)
    if filter_category != 'all':
        query = query.filter_by(category=filter_category)

    transactions = query.order_by(Transaction.transaction_date.desc()).paginate(
        page=page,
        per_page=20,
        error_out=False
    )

    # Get unique categories for filter
    categories = db.session.query(Transaction.category).distinct().all()
    categories = [c[0] for c in categories]

    return render_template('finance/transactions.html',
                         transactions=transactions,
                         filter_type=filter_type,
                         filter_status=filter_status,
                         filter_category=filter_category,
                         categories=categories)


@finance_bp.route('/view/<int:transaction_id>')
@login_required
def view(transaction_id):
    """View transaction details"""
    transaction = Transaction.query.get_or_404(transaction_id)
    return render_template('finance/view.html', transaction=transaction)


@finance_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create new transaction"""
    patients = Patient.query.filter_by(is_active=True).order_by(Patient.first_name).all()

    if request.method == 'POST':
        transaction_type = request.form.get('transaction_type')
        category = request.form.get('category')
        amount = request.form.get('amount')
        description = request.form.get('description')

        if not all([transaction_type, category, amount, description]):
            flash('Please fill in all required fields.', 'danger')
            return render_template('finance/create.html', patients=patients)

        # Create transaction
        transaction = Transaction(
            transaction_type=transaction_type,
            category=category,
            amount=float(amount),
            description=description,
            patient_id=int(request.form.get('patient_id')) if request.form.get('patient_id') else None,
            appointment_id=int(request.form.get('appointment_id')) if request.form.get('appointment_id') else None,
            created_by_id=current_user.id,
            payment_method=request.form.get('payment_method'),
            payment_reference=request.form.get('payment_reference'),
            status=request.form.get('status', 'completed'),
            notes=request.form.get('notes'),
            currency=request.form.get('currency', 'USD')
        )

        # Generate invoice number if it's income
        if transaction_type == 'income':
            transaction.invoice_number = Transaction.generate_invoice_number()

        db.session.add(transaction)
        db.session.commit()

        flash('Transaction created successfully!', 'success')
        return redirect(url_for('finance.view', transaction_id=transaction.id))

    return render_template('finance/create.html', patients=patients)


@finance_bp.route('/edit/<int:transaction_id>', methods=['GET', 'POST'])
@login_required
def edit(transaction_id):
    """Edit transaction"""
    transaction = Transaction.query.get_or_404(transaction_id)
    patients = Patient.query.filter_by(is_active=True).order_by(Patient.first_name).all()

    if request.method == 'POST':
        transaction.transaction_type = request.form.get('transaction_type')
        transaction.category = request.form.get('category')
        transaction.amount = float(request.form.get('amount'))
        transaction.description = request.form.get('description')
        transaction.patient_id = int(request.form.get('patient_id')) if request.form.get('patient_id') else None
        transaction.payment_method = request.form.get('payment_method')
        transaction.payment_reference = request.form.get('payment_reference')
        transaction.status = request.form.get('status')
        transaction.notes = request.form.get('notes')

        db.session.commit()

        flash('Transaction updated successfully!', 'success')
        return redirect(url_for('finance.view', transaction_id=transaction.id))

    return render_template('finance/edit.html', transaction=transaction, patients=patients)


@finance_bp.route('/complete/<int:transaction_id>', methods=['POST'])
@login_required
def complete(transaction_id):
    """Mark transaction as completed"""
    transaction = Transaction.query.get_or_404(transaction_id)

    if transaction.complete():
        flash('Transaction marked as completed.', 'success')
    else:
        flash('Could not complete this transaction.', 'danger')

    return redirect(url_for('finance.view', transaction_id=transaction_id))


@finance_bp.route('/cancel/<int:transaction_id>', methods=['POST'])
@login_required
def cancel(transaction_id):
    """Cancel transaction"""
    transaction = Transaction.query.get_or_404(transaction_id)

    if transaction.cancel():
        flash('Transaction cancelled.', 'success')
    else:
        flash('Could not cancel this transaction.', 'danger')

    return redirect(url_for('finance.view', transaction_id=transaction_id))


@finance_bp.route('/reports')
@login_required
def reports():
    """Financial reports"""
    # This will be implemented with charts and detailed reports
    return render_template('finance/reports.html')
