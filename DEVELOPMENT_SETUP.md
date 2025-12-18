# Development Setup Guide

## 1. After Git Pull

```bash
# Pull latest changes from remote
git pull origin main

# Navigate to project directory
cd django-microfinance-mpsa
```

## 2. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your actual values
nano .env  # or use your preferred editor
```

### Required .env Configuration:

```env
# Django Configuration
DEBUG=True
SECRET_KEY=your-django-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database Configuration (PostgreSQL)
DATABASE_URL=postgresql://flexifinance_user:flexifinance_password@localhost:5432/flexifinance

# For WSL users: See WSL_POSTGRESQL_SETUP.md for detailed PostgreSQL installation and database creation instructions

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_SECRET_KEY=your-supabase-secret-key

# M-Pesa Configuration
MPESA_CONSUMER_KEY=your-mpesa-consumer-key
MPESA_CONSUMER_SECRET=your-mpesa-consumer-secret
MPESA_SHORTCODE=your-mpesa-shortcode
MPESA_PASSKEY=your-mpesa-passkey
MPESA_INITIATOR_NAME=FlexiFinance
MPESA_ENVIRONMENT=sandbox

# IMPORTANT: Update these with your actual ngrok URL
MPESA_CONFIRMATION_URL=https://your-app.ngrok-free.app/api/payments/mpesa/callback/
MPESA_VALIDATION_URL=https://your-app.ngrok-free.app/api/payments/mpesa/validate/

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
```

## 3. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Or if using uv
uv pip install -r requirements.txt
```

## 4. Database Setup

### For WSL Users:
**Follow the detailed guide in `WSL_POSTGRESQL_SETUP.md`** for:
- Installing PostgreSQL on WSL
- Creating the `flexifinance_user` and `flexifinance` database
- Setting up proper permissions

### Quick WSL Setup:
```bash
# Run the automated setup script
chmod +x ~/setup_postgres.sh
~/setup_postgres.sh
```

### For Other Platforms:
```bash
# Install PostgreSQL (Ubuntu/Debian)
sudo apt install postgresql postgresql-contrib

# Create database and user (as postgres user)
sudo -u postgres createdb flexifinance
sudo -u postgres createuser --interactive

# Or using createdb directly
createdb flexifinance
```

### Run Django Migrations:
```bash
# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

## 5. For Development/Testing with ngrok:

### Step 5.1: Install ngrok

```bash
# Download ngrok (if not already installed)
# Visit: https://ngrok.com/download for your OS

# Or using package managers:
# Ubuntu/Debian:
sudo apt update
sudo apt install ngrok

# macOS (Homebrew):
brew install ngrok

# Windows (Chocolatey):
choco install ngrok
```

### Step 5.2: Configure ngrok

```bash
# Sign up at https://ngrok.com and get your authtoken
ngrok config add-autoken YOUR_NGROK_AUTHTOKEN
```

### Step 5.3: Start ngrok

```bash
# Start ngrok tunnel for Django development server (port 8000)
ngrok http 8000

# This will show you a public URL like:
# https://abc123.ngrok-free.app
# https://abc123.ngrok-free.app -> http://localhost:8000
```

### Step 5.4: Update .env with ngrok URL

```bash
# Stop the current ngrok session (Ctrl+C)
# Update your .env file with the new ngrok URL:
nano .env

# Update these lines with your actual ngrok URL:
MPESA_CONFIRMATION_URL=https://abc123.ngrok-free.app/api/payments/mpesa/callback/
MPESA_VALIDATION_URL=https://abc123.ngrok-free.app/api/payments/mpesa/validate/
```

### Step 5.5: Update M-Pesa Portal (Important!)

1. **Go to Safaricom M-Pesa Portal:**
   - Visit: https://developer.safaricom.co.ke/
   - Log in to your developer account

2. **Update Callback URLs:**
   - Go to your app settings
   - Update the following URLs with your ngrok URL:
     - **Confirmation URL:** `https://abc123.ngrok-free.app/api/payments/mpesa/callback/`
     - **Validation URL:** `https://abc123.ngrok-free.app/api/payments/mpesa/validate/`

3. **Save Changes**

### Step 5.6: Start Development Server

```bash
# Start Django development server
python manage.py runserver 0.0.0.0:8000

# In a new terminal, start ngrok again
ngrok http 8000
```

### Step 5.7: Test M-Pesa Integration

1. **Open your browser to:** `http://localhost:8000`
2. **Navigate to payments section**
3. **Test STK Push functionality**
4. **Check ngrok dashboard:** `https://dashboard.ngrok.com` for request logs

## 6. Important Notes for ngrok:

### Keep ngrok Running:
- **ngrok sessions expire after 8 hours**
- **Restart ngrok when session expires**
- **Update M-Pesa portal if URL changes**
- **Always check ngrok dashboard for failed callbacks**

### Security:
- **Never commit real credentials to git**
- **Use different ngrok URLs for different environments**
- **Disable ngrok in production**

### Troubleshooting:

```bash
# Check if Django is running
curl http://localhost:8000/admin/

# Check if ngrok is working
curl https://abc123.ngrok-free.app/admin/

# View ngrok logs
ngrok logs
```

## 7. Production Deployment Preparation:

When you're ready for production with flexifinance.com domain:

```bash
# Update .env for production:
DEBUG=False
ALLOWED_HOSTS=flexifinance.com,www.flexifinance.com

# Update M-Pesa URLs:
MPESA_CONFIRMATION_URL=https://flexifinance.com/api/payments/mpesa/callback/
MPESA_VALIDATION_URL=https://flexifinance.com/api/payments/mpesa/validate/

# Update M-Pesa portal with production URLs
```

## 8. Quick Commands Reference:

```bash
# Development workflow
git pull origin main
python manage.py migrate
ngrok http 8000
# Update .env with ngrok URL
python manage.py runserver 0.0.0.0:8000

# Testing
curl http://localhost:8000/admin/
curl https://abc123.ngrok-free.app/admin/
```