#!/bin/bash

# FlexiFinance Development Environment Setup Script
# This script automates the initial setup process

echo "🚀 FlexiFinance Development Environment Setup"
echo "============================================="

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "❌ Error: manage.py not found. Please run this script from the django-microfinance-mpsa directory."
    exit 1
fi

# Function to prompt for user input with default
prompt_with_default() {
    local prompt="$1"
    local default="$2"
    local varname="$3"
    
    echo -n "$prompt [$default]: "
    read input
    if [ -z "$input" ]; then
        eval "$varname='$default'"
    else
        eval "$varname='$input'"
    fi
}

echo ""
echo "📋 Configuration Setup"
echo "====================="

# Prompt for configuration values
prompt_with_default "Django Secret Key" "django-insecure-change-me" DJANGO_SECRET_KEY
prompt_with_default "Supabase URL" "" SUPABASE_URL
prompt_with_default "Supabase Anon Key" "" SUPABASE_ANON_KEY
prompt_with_default "Supabase Secret Key" "" SUPABASE_SECRET_KEY
prompt_with_default "M-Pesa Consumer Key" "" MPESA_CONSUMER_KEY
prompt_with_default "M-Pesa Consumer Secret" "" MPESA_CONSUMER_SECRET
prompt_with_default "M-Pesa Shortcode" "174379" MPESA_SHORTCODE
prompt_with_default "M-Pesa Passkey" "" MPESA_PASSKEY
prompt_with_default "Email Host User" "" EMAIL_HOST_USER
prompt_with_default "Email Host Password" "" EMAIL_HOST_PASSWORD

echo ""
echo "🔧 Installing Dependencies"
echo "========================="

# Install Python dependencies
if command -v uv &> /dev/null; then
    echo "📦 Using uv for package management..."
    uv pip install -r requirements.txt
else
    echo "📦 Using pip for package management..."
    pip install -r requirements.txt
fi

echo ""
echo "🗄️  PostgreSQL Setup"
echo "==================="

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "📦 Installing PostgreSQL..."
    sudo apt update
    sudo apt install postgresql postgresql-contrib -y
    sudo service postgresql start
    sudo systemctl enable postgresql
fi

# Create database and user
echo "🔐 Creating database user and database..."
sudo -u postgres psql << EOF
DROP USER IF EXISTS flexifinance_user;
CREATE USER flexifinance_user WITH PASSWORD 'flexifinance_password';
DROP DATABASE IF EXISTS flexifinance;
CREATE DATABASE flexifinance OWNER flexifinance_user;
GRANT ALL PRIVILEGES ON DATABASE flexifinance TO flexifinance_user;
\q
EOF

echo "✅ Database setup complete!"

echo ""
echo "📝 Creating .env file"
echo "===================="

# Create .env file
cat > .env << EOF
# Django Configuration
DEBUG=True
SECRET_KEY=$DJANGO_SECRET_KEY
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database Configuration
DATABASE_URL=postgresql://flexifinance_user:flexifinance_password@localhost:5432/flexifinance

# Supabase Configuration
SUPABASE_URL=$SUPABASE_URL
SUPABASE_ANON_KEY=$SUPABASE_ANON_KEY
SUPABASE_SECRET_KEY=$SUPABASE_SECRET_KEY

# M-Pesa Configuration
MPESA_CONSUMER_KEY=$MPESA_CONSUMER_KEY
MPESA_CONSUMER_SECRET=$MPESA_CONSUMER_SECRET
MPESA_SHORTCODE=$MPESA_SHORTCODE
MPESA_PASSKEY=$MPESA_PASSKEY
MPESA_INITIATOR_NAME=FlexiFinance
MPESA_ENVIRONMENT=sandbox

# IMPORTANT: Update these with your actual ngrok URL
MPESA_CONFIRMATION_URL=https://your-app.ngrok-free.app/api/payments/mpesa/callback/
MPESA_VALIDATION_URL=https://your-app.ngrok-free.app/api/payments/mpesa/validate/

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_PORT=587
EMAIL_HOST_USER=$EMAIL_HOST_USER
EMAIL_HOST_PASSWORD=$EMAIL_HOST_PASSWORD
EMAIL_USE_TLS=True
EOF

echo "✅ .env file created!"

echo ""
echo "🗃️  Database Migrations"
echo "======================"

# Run migrations
python manage.py migrate

echo ""
echo "🔑 Creating Superuser"
echo "===================="

# Create superuser
python manage.py createsuperuser

echo ""
echo "🔧 ngrok Setup (Optional for M-Pesa testing)"
echo "============================================"

if ! command -v ngrok &> /dev/null; then
    echo "📦 Installing ngrok..."
    sudo apt install ngrok -y
    
    echo ""
    echo "⚠️  Please configure ngrok with your authtoken:"
    echo "   ngrok config add-autoken YOUR_NGROK_AUTHTOKEN"
    echo ""
    echo "   Get your authtoken from: https://dashboard.ngrok.com/get-started/your-authtoken"
else
    echo "✅ ngrok is already installed!"
fi

echo ""
echo "🎉 Setup Complete!"
echo "=================="

echo ""
echo "📚 Next Steps:"
echo "1. Configure ngrok: ngrok config add-autoken YOUR_NGROK_AUTHTOKEN"
echo "2. Start ngrok: ngrok http 8000"
echo "3. Update .env with your ngrok URL for M-Pesa callbacks"
echo "4. Start development server: python manage.py runserver 0.0.0.0:8000"
echo "5. Update M-Pesa portal with your ngrok URL"
echo ""
echo "🌐 Access your application at: http://localhost:8000"
echo "🔧 Admin panel at: http://localhost:8000/admin"
echo ""
echo "📖 For detailed instructions, see:"
echo "   - DEVELOPMENT_SETUP.md (comprehensive guide)"
echo "   - WSL_POSTGRESQL_SETUP.md (WSL-specific instructions)"
echo "   - QUICK_START.md (quick reference)"
echo ""
echo "Happy coding! 🚀"