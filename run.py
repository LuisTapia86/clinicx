import os
from app import create_app, db
from app.models import User, Patient, MedicalRecord, Appointment, Transaction, Referral

# Create Flask application
app = create_app(os.getenv('FLASK_ENV') or 'development')


@app.shell_context_processor
def make_shell_context():
    """Make database models available in Flask shell"""
    return {
        'db': db,
        'User': User,
        'Patient': Patient,
        'MedicalRecord': MedicalRecord,
        'Appointment': Appointment,
        'Transaction': Transaction,
        'Referral': Referral
    }


@app.cli.command()
def init_db():
    """Initialize the database with tables"""
    db.create_all()
    print("Database initialized successfully!")


@app.cli.command()
def create_admin():
    """Create an admin user"""
    username = input("Enter username: ")
    email = input("Enter email: ")
    password = input("Enter password: ")
    first_name = input("Enter first name: ")
    last_name = input("Enter last name: ")

    # Check if user already exists
    if User.query.filter_by(username=username).first():
        print(f"Error: User '{username}' already exists!")
        return

    # Create admin user
    admin = User(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        role='admin',
        phone='0000000000'
    )
    admin.set_password(password)

    db.session.add(admin)
    db.session.commit()

    print(f"Admin user '{username}' created successfully!")


@app.cli.command()
def seed_db():
    """Seed database with sample data for testing"""
    from datetime import datetime, timedelta
    import random

    print("Seeding database with sample data...")

    # Create sample patients
    patients_data = [
        {"first_name": "John", "last_name": "Doe", "gender": "male", "phone": "555-0101"},
        {"first_name": "Jane", "last_name": "Smith", "gender": "female", "phone": "555-0102"},
        {"first_name": "Michael", "last_name": "Johnson", "gender": "male", "phone": "555-0103"},
        {"first_name": "Emily", "last_name": "Williams", "gender": "female", "phone": "555-0104"},
        {"first_name": "David", "last_name": "Brown", "gender": "male", "phone": "555-0105"},
    ]

    patients = []
    for data in patients_data:
        patient = Patient(
            first_name=data["first_name"],
            last_name=data["last_name"],
            date_of_birth=(datetime.utcnow() - timedelta(days=random.randint(7000, 25000))).date(),
            gender=data["gender"],
            phone=data["phone"],
            email=f"{data['first_name'].lower()}.{data['last_name'].lower()}@email.com",
            blood_type=random.choice(['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'])
        )
        db.session.add(patient)
        patients.append(patient)

    db.session.commit()
    print(f"Created {len(patients)} sample patients")

    # Get admin user
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        print("Error: No admin user found. Create an admin user first!")
        return

    # Create sample appointments
    for patient in patients:
        for i in range(random.randint(1, 3)):
            appointment = Appointment(
                patient_id=patient.id,
                created_by_id=admin.id,
                appointment_date=datetime.utcnow() + timedelta(days=random.randint(1, 30)),
                duration_minutes=random.choice([30, 45, 60]),
                appointment_type=random.choice(['consultation', 'follow_up', 'emergency']),
                reason=random.choice(['Regular checkup', 'Follow-up visit', 'New symptoms', 'Prescription refill']),
                status=random.choice(['scheduled', 'confirmed']),
                cost=random.choice([50.0, 75.0, 100.0, 150.0])
            )
            db.session.add(appointment)

    db.session.commit()
    print("Created sample appointments")

    # Create sample transactions
    categories_income = ['consultation', 'surgery', 'laboratory', 'medication']
    categories_expense = ['supplies', 'salary', 'rent', 'utilities', 'equipment']

    for i in range(20):
        transaction_type = random.choice(['income', 'expense'])
        transaction = Transaction(
            transaction_type=transaction_type,
            category=random.choice(categories_income if transaction_type == 'income' else categories_expense),
            amount=random.uniform(50, 500),
            description=f"Sample {transaction_type} transaction {i+1}",
            patient_id=random.choice(patients).id if transaction_type == 'income' else None,
            created_by_id=admin.id,
            payment_method=random.choice(['cash', 'card', 'transfer']),
            status=random.choice(['completed', 'pending']),
            currency='USD'
        )
        if transaction_type == 'income':
            transaction.invoice_number = Transaction.generate_invoice_number()
        db.session.add(transaction)

    db.session.commit()
    print("Created sample transactions")

    print("Database seeded successfully!")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
