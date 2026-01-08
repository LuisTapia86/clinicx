# ClinicX - Medical Clinic Management System

A comprehensive web-based medical clinic management system built with Flask, designed to manage patients, medical records, appointments, and financial transactions.

## Features

### Patient Management
- Complete patient registration with personal and medical information
- Patient search and filtering
- Medical history tracking
- Emergency contact information
- Insurance details management

### Medical Records
- Comprehensive medical history for each patient
- Vital signs tracking (temperature, blood pressure, heart rate, etc.)
- Diagnosis and treatment documentation
- Prescription management
- Lab and imaging results
- Follow-up scheduling
- BMI calculation and health alerts

### Appointment Scheduling
- Calendar-based appointment scheduling
- Conflict detection
- Multiple appointment statuses (scheduled, confirmed, in progress, completed, cancelled, no-show)
- Appointment types and categories
- Patient appointment history

### Financial Management
- Income and expense tracking
- Multiple payment methods
- Invoice generation
- Transaction categorization
- Financial reports and analytics
- Pending payment tracking
- Balance calculations

### User Management
- Role-based access control (Admin, Doctor, Receptionist)
- Secure authentication
- User activity tracking
- Profile management

### Multi-language Support
- Spanish and English language support (using Flask-Babel)
- Easy language switching

## Technology Stack

- **Backend:** Flask (Python 3.8+)
- **Database:** SQLite (easily upgradable to PostgreSQL)
- **ORM:** SQLAlchemy
- **Authentication:** Flask-Login
- **Internationalization:** Flask-Babel
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup Instructions

1. **Clone or download the project**
   ```bash
   cd ClinicX
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Initialize the database**
   ```bash
   python run.py init_db
   ```

6. **Run the application**
   ```bash
   python run.py
   ```

7. **Access the application**
   - Open your browser and navigate to: `http://localhost:5000`
   - Default admin credentials:
     - Username: `admin`
     - Password: `admin123`
   - **IMPORTANT:** Change the default password after first login!

## Configuration

### Environment Variables
Create a `.env` file in the root directory to customize settings:

```env
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///clinicx.db
```

### Configuration Options
Edit `config.py` to modify:
- Database settings
- Upload folder location
- Session timeout
- Pagination settings
- Supported languages

## Usage

### Creating Your First Patient
1. Log in with admin credentials
2. Navigate to "Patients" → "Create New Patient"
3. Fill in patient information
4. Click "Save"

### Scheduling an Appointment
1. Navigate to "Appointments" → "Create New Appointment"
2. Select patient
3. Choose date and time
4. Add appointment details
5. Click "Schedule"

### Adding Medical Records
1. Navigate to a patient's profile
2. Click "Medical Records" → "Add New Record"
3. Fill in visit details, vital signs, diagnosis, and treatment
4. Click "Save"

### Managing Finances
1. Navigate to "Finance" → "Create Transaction"
2. Select transaction type (income/expense)
3. Fill in details
4. Click "Save"

## CLI Commands

### Initialize Database
```bash
python run.py init_db
```

### Create Admin User
```bash
python run.py create_admin
```

### Seed Database with Sample Data
```bash
python run.py seed_db
```

### Flask Shell (for database operations)
```bash
flask shell
```

## Database Models

### Core Models
- **User:** System users with role-based access
- **Patient:** Patient information and demographics
- **MedicalRecord:** Medical history and visit records
- **Appointment:** Appointment scheduling and management
- **Transaction:** Financial transactions (income/expenses)

### Relationships
- Patient → Medical Records (One-to-Many)
- Patient → Appointments (One-to-Many)
- Patient → Transactions (One-to-Many)
- User → Appointments (created_by, One-to-Many)
- User → Transactions (created_by, One-to-Many)
- Appointment → Transactions (Optional One-to-Many)

## Security Features

- Password hashing using Werkzeug
- CSRF protection with Flask-WTF
- Session management with Flask-Login
- Role-based access control
- Secure file upload handling

## Project Structure

```
ClinicX/
├── app/
│   ├── __init__.py              # Flask app initialization
│   ├── models/                  # Database models
│   │   ├── user.py
│   │   ├── patient.py
│   │   ├── medical_record.py
│   │   ├── appointment.py
│   │   └── transaction.py
│   ├── auth/                    # Authentication module
│   ├── patients/                # Patient management module
│   ├── medical/                 # Medical records module
│   ├── appointments/            # Appointments module
│   ├── finance/                 # Finance module
│   ├── static/                  # CSS, JS, images
│   ├── templates/               # HTML templates
│   └── utils/                   # Utility functions
├── config.py                    # Configuration settings
├── run.py                       # Application entry point
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Contributing

This is a private project, but suggestions and improvements are welcome.

## License

Proprietary - All rights reserved

## Support

For issues or questions, please contact the development team.

## Changelog

### Version 1.0.0 (Initial Release)
- Patient management system
- Medical records tracking
- Appointment scheduling
- Financial transaction management
- User authentication and role-based access
- Multi-language support (Spanish/English)
