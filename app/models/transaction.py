from datetime import datetime
from app import db


class Transaction(db.Model):
    """Transaction model for managing income and expenses"""

    __tablename__ = 'transactions'

    # Primary Key
    id = db.Column(db.Integer, primary_key=True)

    # Foreign Keys
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=True, index=True)  # Nullable for expenses
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=True, index=True)  # Optional link
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    # Transaction Information
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Type: 'income' or 'expense'
    transaction_type = db.Column(db.String(20), nullable=False, index=True)

    # Category: 'consultation', 'surgery', 'medication', 'laboratory', 'supplies', 'salary', 'rent', 'utilities', etc.
    category = db.Column(db.String(64), nullable=False, index=True)

    # Amount
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='USD', nullable=False)  # ISO currency code

    # Payment Information
    payment_method = db.Column(db.String(32))  # 'cash', 'card', 'transfer', 'check', 'insurance'
    payment_reference = db.Column(db.String(128))  # Receipt number, transaction ID, check number, etc.

    # Status: 'pending', 'completed', 'cancelled', 'refunded'
    status = db.Column(db.String(20), default='completed', nullable=False, index=True)

    # Description
    description = db.Column(db.String(256), nullable=False)
    notes = db.Column(db.Text)

    # Invoice/Receipt
    invoice_number = db.Column(db.String(64), unique=True, index=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = db.Column(db.DateTime)
    cancelled_at = db.Column(db.DateTime)

    # Relationships
    appointment = db.relationship('Appointment', backref='transactions', foreign_keys=[appointment_id])

    def __repr__(self):
        return f'<Transaction {self.transaction_type} ${self.amount} - {self.category}>'

    def is_income(self):
        """Check if transaction is income"""
        return self.transaction_type == 'income'

    def is_expense(self):
        """Check if transaction is expense"""
        return self.transaction_type == 'expense'

    def is_completed(self):
        """Check if transaction is completed"""
        return self.status == 'completed'

    def is_pending(self):
        """Check if transaction is pending"""
        return self.status == 'pending'

    def complete(self):
        """Mark transaction as completed"""
        if self.status == 'pending':
            self.status = 'completed'
            self.completed_at = datetime.utcnow()
            db.session.commit()
            return True
        return False

    def cancel(self):
        """Cancel the transaction"""
        if self.status in ['pending', 'completed']:
            self.status = 'cancelled'
            self.cancelled_at = datetime.utcnow()
            db.session.commit()
            return True
        return False

    def refund(self):
        """Refund the transaction"""
        if self.status == 'completed' and self.is_income():
            self.status = 'refunded'
            db.session.commit()
            return True
        return False

    @staticmethod
    def generate_invoice_number():
        """Generate a unique invoice number"""
        # Format: INV-YYYYMMDD-XXXX
        today = datetime.utcnow()
        prefix = today.strftime('INV-%Y%m%d')

        # Get the last invoice number for today
        last_transaction = Transaction.query.filter(
            Transaction.invoice_number.like(f'{prefix}%')
        ).order_by(Transaction.invoice_number.desc()).first()

        if last_transaction:
            last_number = int(last_transaction.invoice_number.split('-')[-1])
            new_number = last_number + 1
        else:
            new_number = 1

        return f'{prefix}-{new_number:04d}'

    @staticmethod
    def get_total_income(start_date=None, end_date=None, status='completed'):
        """Calculate total income for a period"""
        query = Transaction.query.filter(
            Transaction.transaction_type == 'income',
            Transaction.status == status
        )

        if start_date:
            query = query.filter(Transaction.transaction_date >= start_date)
        if end_date:
            query = query.filter(Transaction.transaction_date <= end_date)

        total = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.id.in_([t.id for t in query.all()])
        ).scalar()

        return total or 0.0

    @staticmethod
    def get_total_expenses(start_date=None, end_date=None, status='completed'):
        """Calculate total expenses for a period"""
        query = Transaction.query.filter(
            Transaction.transaction_type == 'expense',
            Transaction.status == status
        )

        if start_date:
            query = query.filter(Transaction.transaction_date >= start_date)
        if end_date:
            query = query.filter(Transaction.transaction_date <= end_date)

        total = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.id.in_([t.id for t in query.all()])
        ).scalar()

        return total or 0.0

    @staticmethod
    def get_balance(start_date=None, end_date=None):
        """Calculate balance (income - expenses)"""
        income = Transaction.get_total_income(start_date, end_date)
        expenses = Transaction.get_total_expenses(start_date, end_date)
        return income - expenses
