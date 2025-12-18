# Step-by-Step Setup Commands

Execute these commands in your WSL terminal after `git pull origin main`:

## 1. Navigate to Project Directory
```bash
# Pull latest changes from GitHub
git pull origin main

# Navigate to project directory
cd django-microfinance-mpsa
```

## 2. PostgreSQL Setup (Choose One Method)

### Method A: Automated Setup (Recommended)
```bash
# Make script executable
chmod +x setup_postgres_only.sh

# Run PostgreSQL setup
./setup_postgres_only.sh
```

### Method B: Manual Setup
```bash
# Check if PostgreSQL is already installed
which psql
sudo service postgresql status

# If not installed, install it:
sudo apt update && sudo apt install postgresql postgresql-contrib -y

# Start PostgreSQL service
sudo service postgresql start
sudo systemctl enable postgresql

# Create database and user
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
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your credentials
nano .env  # or use your preferred editor
```

### Required .env Configuration:
```env
# Django Configuration
DEBUG=True
SECRET_KEY=your-django-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database Configuration
DATABASE_URL=postgresql://flexifinance_user:flexifinance_password@localhost:5432/flexifinance

# Supabase Configuration (add your actual values)
SUPABASE_URL=your-supabase-url
SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_SECRET_KEY=your-supabase-secret-key

# M-Pesa Configuration (add your actual values)
MPESA_CONSUMER_KEY=your-mpesa-consumer-key
MPESA_CONSUMER_SECRET=your-mpesa-consumer-secret
MPESA_SHORTCODE=174379
MPESA_PASSKEY=your-mpesa-passkey
MPESA_INITIATOR_NAME=FlexiFinance
MPESA_ENVIRONMENT=sandbox

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
```

## 4. Install Dependencies
```bash
# Install Python dependencies
pip install -r requirements.txt

# Or if using uv
uv pip install -r requirements.txt
```

## 5. Database Migrations
```bash
# Run Django migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

## 6. ngrok Setup (for M-Pesa Testing)

### Step 6.1: Install ngrok
```bash
# Check if ngrok is already installed
which ngrok

# If not installed, install it:
sudo apt install ngrok
```

### Step 6.2: Configure ngrok
```bash
# Add your ngrok authtoken
ngrok config add-autoken YOUR_NGROK_AUTHTOKEN
```

### Step 6.3: Start ngrok
```bash
# Start ngrok tunnel
ngrok http 8000
```

### Step 6.4: Update .env with ngrok URL
```bash
# Update .env with the ngrok URL shown (e.g., https://abc123.ngrok-free.app)
nano .env

# Update these lines:
MPESA_CONFIRMATION_URL=https://abc123.ngrok-free.app/api/payments/mpesa/callback/
MPESA_VALIDATION_URL=https://abc123.ngrok-free.app/api/payments/mpesa/validate/
```

## 7. Update M-Pesa Portal
1. Go to https://developer.safaricom.co.ke/
2. Log in to your developer account
3. Navigate to your app settings
4. Update callback URLs:
   - **Confirmation URL:** `https://abc123.ngrok-free.app/api/payments/mpesa/callback/`
   - **Validation URL:** `https://abc123.ngrok-free.app/api/payments/mpesa/validate/`
5. Save changes

## 8. Start Development Server
```bash
# Start Django development server
python manage.py runserver 0.0.0.0:8000
```

## 9. Test Everything

### 9.1: Test Django Application
```bash
# In a new terminal, test Django
curl http://localhost:8000/admin/
```

### 9.2: Test ngrok
```bash
# Test ngrok tunnel (replace abc123 with your actual URL)
curl https://abc123.ngrok-free.app/admin/
```

### 9.3: Test Database Connection
```bash
# Test database connection
psql -h localhost -U flexifinance_user -d flexifinance -c "SELECT current_database(), current_user;"
```

## 10. Access Your Application

- **Application:** http://localhost:8000
- **Admin Panel:** http://localhost:8000/admin
- **ngrok Dashboard:** https://dashboard.ngrok.com

## Troubleshooting Commands

### Check PostgreSQL Status
```bash
sudo service postgresql status
psql --version
```

### Check Django Status
```bash
python manage.py check
python manage.py runserver 0.0.0.0:8000
```

### Check ngrok Status
```bash
ngrok status
ngrok logs
```

### View Application Logs
```bash
# Django logs (when running server)
# ngrok logs (from ngrok dashboard)
```

## Files Created for You

All setup guides have been created and pushed to GitHub:

- `DEVELOPMENT_SETUP.md` - Comprehensive setup guide
- `WSL_POSTGRESQL_SETUP.md` - WSL-specific PostgreSQL guide
- `QUICK_START.md` - Quick reference commands
- `setup_dev_environment.sh` - Full environment setup script
- `setup_postgres_only.sh` - PostgreSQL-only setup script
- `STEP_BY_STEP_SETUP.md` - This step-by-step guide

## Next Steps

1. Execute the commands above in order
2. Configure your ngrok URL in the M-Pesa portal
3. Test the M-Pesa integration
4. Start developing your features!

Happy coding! 🚀