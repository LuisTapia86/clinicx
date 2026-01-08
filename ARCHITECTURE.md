# ClinicX - System Architecture Documentation

## Overview

ClinicX is built using a modular architecture with Flask blueprints, ensuring clean separation of concerns and maintainability. All modules are connected through shared database models and relationships.

## Architecture Pattern

### Model-View-Controller (MVC) Pattern
- **Models:** SQLAlchemy ORM models in `app/models/`
- **Views:** Flask blueprints and route handlers in each module
- **Templates:** Jinja2 HTML templates in `app/templates/`

### Modular Blueprint Architecture
Each feature is organized as a Flask blueprint:
- `auth` - Authentication and user management
- `patients` - Patient management
- `medical` - Medical records
- `appointments` - Appointment scheduling
- `finance` - Financial transactions

## Database Architecture

### Entity Relationship Diagram

```
┌─────────────┐
│    User     │
│  (System)   │
└──────┬──────┘
       │ created_by
       │
       ├──────────────┐
       │              │
       ▼              ▼
┌─────────────┐  ┌─────────────┐
│ Appointment │  │ Transaction │
└──────┬──────┘  └──────┬──────┘
       │                │
       │ patient_id     │ patient_id
       │                │
       ├────────────────┤
       │                │
       ▼                ▼
┌─────────────────────────┐
│       Patient           │
└────────┬────────────────┘
         │
         │ patient_id
         ▼
┌─────────────────────┐
│   MedicalRecord     │
└─────────────────────┘
```

### Model Descriptions

#### User
- **Purpose:** System users (admin, doctor, receptionist)
- **Key Fields:** username, email, password_hash, role, is_active
- **Relationships:**
  - appointments_created (one-to-many with Appointment)
  - transactions_created (one-to-many with Transaction)

#### Patient
- **Purpose:** Patient demographics and contact information
- **Key Fields:** name, date_of_birth, gender, contact info, insurance, allergies
- **Relationships:**
  - medical_records (one-to-many with MedicalRecord)
  - appointments (one-to-many with Appointment)
  - transactions (one-to-many with Transaction)

#### MedicalRecord
- **Purpose:** Medical history and visit documentation
- **Key Fields:** visit_date, diagnosis, treatment, vital_signs, prescription
- **Relationships:**
  - patient (many-to-one with Patient)

#### Appointment
- **Purpose:** Appointment scheduling and tracking
- **Key Fields:** appointment_date, status, reason, duration, cost
- **Relationships:**
  - patient (many-to-one with Patient)
  - created_by (many-to-one with User)
  - transactions (one-to-many with Transaction)

#### Transaction
- **Purpose:** Financial income and expenses
- **Key Fields:** transaction_type, category, amount, payment_method, status
- **Relationships:**
  - patient (many-to-one with Patient, optional for expenses)
  - appointment (many-to-one with Appointment, optional)
  - created_by (many-to-one with User)

## Module Architecture

### Authentication Module (`app/auth/`)
**Purpose:** User authentication and session management

**Components:**
- Login/Logout functionality
- User profile management
- Password change
- Session management with Flask-Login

**Access Control:**
- Public routes: login
- Protected routes: profile, change_password, logout

### Patients Module (`app/patients/`)
**Purpose:** Patient management and demographics

**Components:**
- Patient CRUD operations
- Patient search and filtering
- Patient profile view with medical history
- Soft delete (deactivation)

**Access Control:**
- All users can view and create patients
- Only admins can delete patients

**Key Features:**
- Age calculation from date_of_birth
- Emergency contact management
- Insurance information
- Medical alerts (allergies, chronic conditions)

### Medical Records Module (`app/medical/`)
**Purpose:** Medical history and visit documentation

**Components:**
- Medical record CRUD operations
- Vital signs tracking
- Diagnosis and treatment documentation
- Follow-up scheduling
- Prescription management

**Access Control:**
- All authenticated users can view records
- Doctors and admins can create/edit records
- Only admins and doctors can delete records

**Key Features:**
- BMI calculation
- Abnormal vital signs detection
- File attachments support (planned)
- Follow-up tracking

### Appointments Module (`app/appointments/`)
**Purpose:** Appointment scheduling and management

**Components:**
- Appointment CRUD operations
- Calendar view
- Conflict detection
- Status management (scheduled, confirmed, in_progress, completed, cancelled, no_show)

**Access Control:**
- All users can view and create appointments
- Status changes require appropriate permissions

**Key Features:**
- Schedule conflict detection
- Appointment duration tracking
- Multiple appointment types
- Reminder system (planned)
- Calendar API for frontend integration

### Finance Module (`app/finance/`)
**Purpose:** Financial transaction management

**Components:**
- Transaction CRUD operations
- Income/Expense tracking
- Invoice generation
- Financial reports
- Balance calculations

**Access Control:**
- All users can view transactions
- Admins have full control
- Financial reports accessible to admins

**Key Features:**
- Automatic invoice number generation
- Payment method tracking
- Transaction status (pending, completed, cancelled, refunded)
- Category-based organization
- Period-based reporting (today, week, month, year)

## Data Flow

### Patient Registration Flow
```
User Input → Validation → Patient Model → Database → Success Response
```

### Appointment Scheduling Flow
```
User Input → Patient Selection → Date/Time Selection → Conflict Check → Appointment Model → Database
```

### Medical Record Creation Flow
```
Patient Selection → Visit Details → Vital Signs → Diagnosis → Treatment → MedicalRecord Model → Database
```

### Transaction Creation Flow
```
Transaction Type → Category → Amount → Patient Link (optional) → Invoice Generation → Transaction Model → Database
```

## Security Architecture

### Authentication
- **Password Storage:** Werkzeug password hashing (PBKDF2 + SHA-256)
- **Session Management:** Flask-Login with secure cookies
- **Session Lifetime:** 24 hours (configurable)

### Authorization
- **Role-Based Access Control (RBAC)**
  - Admin: Full system access
  - Doctor: Medical records, appointments, patient management
  - Receptionist: Patient management, appointments, basic transactions

### Data Protection
- **CSRF Protection:** Flask-WTF CSRF tokens
- **SQL Injection Prevention:** SQLAlchemy ORM parameterized queries
- **XSS Prevention:** Jinja2 auto-escaping
- **File Upload Security:** Extension validation, size limits

## Extension Points

### Adding New Modules
1. Create blueprint in `app/new_module/__init__.py`
2. Define routes in `app/new_module/routes.py`
3. Register blueprint in `app/__init__.py`
4. Add templates in `app/templates/new_module/`

### Adding New Models
1. Create model in `app/models/new_model.py`
2. Import in `app/models/__init__.py`
3. Add relationships to existing models
4. Run database migration

### Adding Internationalization
1. Mark strings with `_('text')` or `gettext('text')`
2. Extract translations: `pybabel extract`
3. Initialize language: `pybabel init -l es`
4. Compile translations: `pybabel compile`

## Performance Considerations

### Database Optimization
- **Indexes:** Added on foreign keys and frequently queried fields
- **Lazy Loading:** Relationships use `lazy='dynamic'` for large datasets
- **Pagination:** List views paginated to 10-20 items per page

### Caching Strategy (Future)
- Session caching for user data
- Query result caching for reports
- Static file caching with versioning

### Scalability
- **Database:** SQLite for development, PostgreSQL for production
- **Application Server:** Gunicorn/uWSGI for production
- **Web Server:** Nginx reverse proxy
- **Load Balancing:** Horizontal scaling ready

## Configuration Management

### Environment-Based Configuration
- **Development:** Debug mode, SQL echoing, relaxed security
- **Production:** Debug off, strict security, performance optimizations
- **Testing:** In-memory database, disabled CSRF

### Configuration Files
- `config.py` - Main configuration classes
- `.env` - Environment variables (not in version control)

## Error Handling

### Application Errors
- 404: Page not found
- 403: Forbidden (insufficient permissions)
- 500: Internal server error

### Database Errors
- Integrity errors (duplicate entries)
- Foreign key violations
- Connection errors

### User Errors
- Form validation errors
- Authentication failures
- Authorization denials

## Logging Strategy (Future Enhancement)

### Log Levels
- **DEBUG:** Development troubleshooting
- **INFO:** Normal operation events
- **WARNING:** Unexpected but handled issues
- **ERROR:** Operation failures
- **CRITICAL:** System failures

### Log Categories
- Authentication events
- Database operations
- User actions
- System errors
- Security events

## Testing Strategy (Future Enhancement)

### Unit Tests
- Model methods
- Utility functions
- Form validation

### Integration Tests
- Route handlers
- Database operations
- Authentication flow

### End-to-End Tests
- User workflows
- Complete feature testing
- Security testing

## Deployment Architecture

### Development
```
Flask Development Server (port 5000) → SQLite Database
```

### Production
```
Nginx → Gunicorn → Flask App → PostgreSQL Database
```

## Future Enhancements

### Planned Features
- Email notifications
- SMS reminders
- Report generation (PDF)
- Advanced analytics dashboard
- API for mobile app integration
- Backup and restore functionality
- Audit trail logging

### Technical Improvements
- Redis caching layer
- Celery task queue for background jobs
- Docker containerization
- CI/CD pipeline
- Automated testing suite
- API documentation (OpenAPI/Swagger)

## Maintenance Guidelines

### Database Migrations
- Use Flask-Migrate (Alembic) for schema changes
- Always backup before migration
- Test migrations in development first

### Code Quality
- Follow PEP 8 style guide
- Use type hints where appropriate
- Write docstrings for all functions
- Keep functions small and focused

### Version Control
- Use Git for version control
- Branch strategy: main/develop/feature branches
- Meaningful commit messages
- Code review before merging

## Troubleshooting

### Common Issues

**Database locked error:**
- SQLite limitation with concurrent writes
- Solution: Upgrade to PostgreSQL for production

**Import errors:**
- Check circular imports in models
- Ensure all `__init__.py` files are present

**Template not found:**
- Verify template path matches blueprint name
- Check template file extension (.html)

**Session not persisting:**
- Verify SECRET_KEY is set
- Check session cookie settings

## Contact

For architecture questions or suggestions, contact the development team.
