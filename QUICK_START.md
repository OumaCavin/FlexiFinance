# Quick Start Guide

## 1. Git Pull & Setup
```bash
git pull origin main
cd django-microfinance-mpsa
cp .env.example .env
```

## 2. WSL PostgreSQL Setup

### Check if PostgreSQL is already installed:
```bash
# Check if PostgreSQL is installed
which psql
sudo service postgresql status
```

### If PostgreSQL is already installed, just start it:
```bash
sudo service postgresql start
sudo systemctl enable postgresql
```

### If PostgreSQL is not installed, install it:
```bash
# Install PostgreSQL
sudo apt update && sudo apt install postgresql postgresql-contrib -y

# Start PostgreSQL service
sudo service postgresql start
sudo systemctl enable postgresql
```

### Setup database (run this regardless):
```bash
sudo -u postgres psql << EOF
DROP USER IF EXISTS flexifinance_user;
DROP DATABASE IF EXISTS flexifinance;
CREATE USER flexifinance_user WITH PASSWORD 'flexifinance_password';
CREATE DATABASE flexifinance OWNER flexifinance_user;
GRANT ALL PRIVILEGES ON DATABASE flexifinance TO flexifinance_user;
\q
EOF

# Test connection
psql -h localhost -U flexifinance_user -d flexifinance -c "SELECT version();"
```

## 3. Environment Configuration
```env
DATABASE_URL=postgresql://flexifinance_user:flexifinance_password@localhost:5432/flexifinance
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Add your M-Pesa, Supabase, and email credentials to .env
```

## 4. Install & Migrate
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
```

## 5. ngrok Setup (for M-Pesa testing)
```bash
# Install ngrok
sudo apt install ngrok

# Configure
ngrok config add-autoken YOUR_NGROK_AUTHTOKEN

# Start ngrok
ngrok http 8000
# Copy the ngrok URL and update .env:
# MPESA_CONFIRMATION_URL=https://abc123.ngrok-free.app/api/payments/mpesa/callback/
# MPESA_VALIDATION_URL=https://abc123.ngrok-free.app/api/payments/mpesa/validate/
```

## 6. Start Development
```bash
python manage.py runserver 0.0.0.0:8000
```

## 7. M-Pesa Portal Update
1. Go to https://developer.safaricom.co.ke/
2. Update callback URLs to your ngrok URL
3. Test STK Push functionality

**Access the application at:** http://localhost:8000