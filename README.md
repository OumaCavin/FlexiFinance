# FlexiFinance - Django MicroFinance Platform

[![Django](https://img.shields.io/badge/Django-5.2.8-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)](https://github.com/OumaCavin/django-microfinance-mpsa)

FlexiFinance is a modern, comprehensive micro-finance platform built with Django and integrated with M-Pesa for seamless loan applications, disbursement, and repayment services. The platform provides a complete solution for micro-finance institutions to manage their operations efficiently.

## 🌟 Features

### Core Features
- **User Management**: Complete user registration, authentication, and profile management
- **KYC Verification**: Document upload and verification system
- **Loan Management**: Loan application, approval, and disbursement workflow
- **M-Pesa Integration**: STK Push, payment processing, and transaction handling
- **Payment Processing**: Secure payment processing with M-Pesa callbacks
- **Admin Dashboard**: Comprehensive admin panel for loan and user management
- **Responsive Design**: Mobile-first design with Bootstrap 5
- **RESTful API**: Complete API with JWT authentication
- **Real-time Notifications**: Email, SMS, and in-app notifications

### Advanced Features
- **Risk Assessment**: Automated credit scoring and risk analysis
- **Document Management**: Secure document upload and verification
- **Audit Trail**: Complete transaction and user action logging
- **Multi-currency Support**: Ready for multiple currencies
- **Security**: CSRF protection, secure authentication, and data encryption
- **Scalable Architecture**: Built for high performance and scalability

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL, MySQL, or SQLite (SQLite for development)
- Redis (optional, for caching)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/OumaCavin/django-microfinance-mpsa.git
   cd django-microfinance-mpsa
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment setup**
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   ```

5. **Database setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Web interface: http://127.0.0.1:8000
   - Admin panel: http://127.0.0.1:8000/admin/
   - API documentation: http://127.0.0.1:8000/api/docs/

## 📋 Documentation

### Complete Documentation Package

This project includes comprehensive documentation:

- **[Project Plan](docs/PROJECT_PLAN.md)** - Project overview, goals, and timeline
- **[Architecture Overview](docs/architecture_overview.md)** - System architecture and design patterns
- **[Use Case Diagram](docs/use_case_diagram.md)** - User stories and system interactions
- **[Sequence Diagram](docs/sequence_diagram.md)** - Detailed process flows
- **[Activity Diagram](docs/activity_diagram.md)** - Workflow processes
- **[Class Diagram](docs/class_diagram.md)** - Data models and relationships
- **[Component Diagram](docs/component_diagram.md)** - System components and integration
- **[Deployment Architecture](docs/deployment_architecture.md)** - Production deployment guide
- **[Multi-Agent System](docs/multi_agent_system.md)** - AI agent design for automation
- **[Onboarding Guide](docs/onboarding_guide.md)** - User onboarding and training
- **[API Reference](docs/api_reference.md)** - Complete API documentation

### Key Documentation Sections

#### For Developers
- **[PyCharm Setup Guide](docs/PYCHARM_SETUP.md)** - IDE configuration and setup
- **[Deployment Guide](docs/deployment_architecture.md)** - Production deployment
- **[API Reference](docs/api_reference.md)** - RESTful API documentation

#### For Users
- **[Onboarding Guide](docs/onboarding_guide.md)** - Step-by-step user guide
- **[User Manual](docs/onboarding_guide.md)** - How to use the platform

#### For Administrators
- **[Admin Guide](docs/PYCHARM_SETUP.md)** - System administration
- **[Security Guide](docs/architecture_overview.md)** - Security implementation

## 🏗️ Project Structure

```
django-microfinance-mpsa/
├── apps/                      # Django applications
│   ├── users/                # User management
│   ├── loans/                # Loan processing
│   ├── payments/             # M-Pesa integration
│   ├── notifications/        # Notification system
│   └── documents/            # Document management
├── templates/                # HTML templates
│   ├── base/                 # Base templates
│   ├── users/                # User templates
│   ├── loans/                # Loan templates
│   ├── payments/             # Payment templates
│   └── admin/                # Admin templates
├── static/                   # Static files
│   ├── css/                  # Stylesheets
│   ├── js/                   # JavaScript files
│   └── images/               # Image assets
├── docs/                     # Documentation
├── flexifinance/             # Django project
│   ├── settings/             # Configuration files
│   ├── urls.py              # URL routing
│   └── wsgi.py              # WSGI configuration
├── requirements.txt          # Python dependencies
├── .env.example             # Environment template
├── README.md                # This file
└── manage.py                # Django management script
```

## 🗄️ Database Configuration

The project supports multiple databases with SQLite as default for development:

### SQLite (Development - Default)
```python
# Default configuration in settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### PostgreSQL (Production)
```python
# Uncomment in settings.py for PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'flexifinance_db',
        'USER': 'flexifinance_user',
        'PASSWORD': 'secure_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### MySQL (Alternative)
```python
# Uncomment in settings.py for MySQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'flexifinance_db',
        'USER': 'flexifinance_user',
        'PASSWORD': 'secure_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

## 🔧 Configuration

### Environment Variables

Key environment variables to configure:

```bash
# Django Settings
SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=flexifinance_db
DB_USER=flexifinance_user
DB_PASSWORD=secure_password

# M-Pesa
MPESA_CONSUMER_KEY=your_consumer_key
MPESA_CONSUMER_SECRET=your_consumer_secret
MPESA_PASSKEY=your_passkey
MPESA_SHORTCODE=174379
MPESA_ENVIRONMENT=sandbox

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
```

### M-Pesa Configuration

1. **Register at Safaricom Developer Portal**
   - Visit: https://developer.safaricom.co.ke/
   - Create account and get API credentials

2. **Configure M-Pesa Settings**
   ```bash
   MPESA_CONSUMER_KEY=your_consumer_key
   MPESA_CONSUMER_SECRET=your_consumer_secret
   MPESA_PASSKEY=your_passkey
   MPESA_SHORTCODE=your_shortcode
   ```

3. **Set Callback URLs**
   - Confirmation URL: `https://yourdomain.com/api/payments/mpesa/callback/`
   - Validation URL: `https://yourdomain.com/api/payments/mpesa/validate/`

## 🎯 Usage

### For Borrowers

1. **Registration**: Create account and complete email verification
2. **KYC**: Upload identification documents for verification
3. **Loan Application**: Apply for loans with preferred terms
4. **Approval**: Receive approval notifications
5. **Disbursement**: Receive funds via M-Pesa
6. **Repayment**: Make payments through M-Pesa STK Push

### For Administrators

1. **User Management**: Manage user accounts and verify KYC
2. **Loan Review**: Review and approve/reject loan applications
3. **Payment Monitoring**: Monitor payment transactions
4. **Report Generation**: Generate various reports and analytics
5. **System Configuration**: Configure loan products and settings

### API Usage

```python
import requests

# Register user
response = requests.post('http://localhost:8000/api/v1/auth/register/', {
    'email': 'user@example.com',
    'password': 'securepassword',
    'first_name': 'John',
    'last_name': 'Doe',
    'phone_number': '+254700123456'
})

# Login to get token
login_response = requests.post('http://localhost:8000/api/v1/auth/login/', {
    'email': 'user@example.com',
    'password': 'securepassword'
})

access_token = login_response.json()['data']['access_token']

# Apply for loan
headers = {'Authorization': f'Bearer {access_token}'}
loan_response = requests.post('http://localhost:8000/api/v1/loans/apply/', {
    'product_id': 'quick_cash',
    'requested_amount': 10000,
    'requested_tenure': 3,
    'purpose': 'Business expansion'
}, headers=headers)
```

## 🧪 Testing

### Run Tests
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.loans

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

### Test Data
```bash
# Create sample data
python manage.py loaddata sample_data.json

# Create test users
python manage.py shell
from apps.users.models import User
User.objects.create_user('test@example.com', 'password', 'John', 'Doe')
```

## 🚀 Deployment

### Production Deployment

#### Using Gunicorn and Nginx
```bash
# Install gunicorn
pip install gunicorn

# Collect static files
python manage.py collectstatic --noinput

# Run with gunicorn
gunicorn flexifinance.wsgi:application --bind 0.0.0.0:8000
```

#### Using Docker
```bash
# Build image
docker build -t flexifinance .

# Run container
docker run -p 8000:8000 --env-file .env flexifinance
```

#### Using Heroku
```bash
# Install Heroku CLI and login
heroku create flexifinance-app
heroku addons:create heroku-postgresql:mini
heroku config:set DEBUG=False
heroku config:set SECRET_KEY=your_production_secret_key
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

### Environment Setup

#### Production Checklist
- [ ] Set `DEBUG=False`
- [ ] Configure `SECRET_KEY`
- [ ] Set up SSL/HTTPS
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set up database (PostgreSQL recommended)
- [ ] Configure email service
- [ ] Set up M-Pesa production environment
- [ ] Configure static file storage
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy

## 📱 Mobile Support

The platform is designed with mobile-first approach:

- **Responsive Design**: Bootstrap 5 responsive components
- **Progressive Web App**: PWA features for mobile installation
- **M-Pesa Integration**: Optimized for mobile payments
- **Touch Interface**: Mobile-friendly interactions
- **Offline Capability**: Basic functionality without internet

## 🔒 Security Features

- **Authentication**: JWT-based authentication with refresh tokens
- **CSRF Protection**: Cross-site request forgery protection
- **SQL Injection Prevention**: ORM-based queries with parameterization
- **XSS Protection**: Template auto-escaping and security headers
- **HTTPS Enforcement**: SSL/TLS encryption for all communications
- **Rate Limiting**: API rate limiting to prevent abuse
- **Input Validation**: Server-side input validation and sanitization
- **Audit Logging**: Comprehensive audit trail for all operations

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

### Code Standards
- Follow PEP 8 Python style guide
- Use Black for code formatting
- Use isort for import sorting
- Write comprehensive tests
- Update documentation

### Git Workflow
```bash
# Configure git (required)
git config user.name "OumaCavin"
git config user.email "cavin.otieno012@gmail.com"

# Standard git workflow
git branch -M main
git add .
git commit -m "feat: add loan approval workflow"
git push origin main
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Getting Help
- **Documentation**: Check the docs folder for comprehensive guides
- **Issues**: Open an issue on GitHub for bugs and feature requests
- **Email**: support@flexifinance.com
- **Phone**: +254 700 123 456

### Community
- **GitHub**: https://github.com/OumaCavin/django-microfinance-mpsa
- **Discussions**: GitHub Discussions for community support

## 🎉 Acknowledgments

- **Django Team** for the excellent web framework
- **Safaricom** for the M-Pesa API documentation
- **Bootstrap Team** for the responsive CSS framework
- **All Contributors** who helped build this platform

## 📈 Roadmap

### Phase 1 (Current)
- [x] Core user management
- [x] Basic loan processing
- [x] M-Pesa integration
- [x] Admin dashboard
- [x] API development

### Phase 2 (Next)
- [ ] Mobile app development (React Native)
- [ ] Advanced risk assessment
- [ ] Multi-loan products
- [ ] Insurance integration
- [ ] Advanced reporting

### Phase 3 (Future)
- [ ] AI-powered loan decisions
- [ ] Blockchain integration
- [ ] Multi-currency support
- [ ] Third-party integrations
- [ ] International expansion

---

**Built with ❤️ by Cavin Otieno**

For more information, visit our [documentation](docs/) or contact us at [info@flexifinance.com](mailto:info@flexifinance.com).
