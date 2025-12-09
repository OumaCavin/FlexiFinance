#!/bin/bash

# PostgreSQL Setup Script for FlexiFinance
# This script only handles PostgreSQL installation and setup

echo "🗄️  FlexiFinance PostgreSQL Setup"
echo "================================="

# Check if we're on a Debian/Ubuntu system
if ! command -v apt &> /dev/null; then
    echo "❌ This script is designed for Debian/Ubuntu systems with apt package manager."
    echo "   Please install PostgreSQL manually for your system."
    exit 1
fi

# Check if PostgreSQL is already installed
if command -v psql &> /dev/null; then
    echo "✅ PostgreSQL is already installed!"
    
    # Check PostgreSQL version
    psql --version
    echo ""
    
    # Check if service is running
    if sudo service postgresql status &> /dev/null; then
        echo "✅ PostgreSQL service is running"
    else
        echo "🔄 Starting PostgreSQL service..."
        sudo service postgresql start
        sudo systemctl enable postgresql
        echo "✅ PostgreSQL service started and enabled"
    fi
else
    echo "📦 PostgreSQL not found. Installing..."
    
    # Update package list
    echo "📦 Updating package list..."
    sudo apt update
    
    # Install PostgreSQL
    echo "📦 Installing PostgreSQL..."
    sudo apt install postgresql postgresql-contrib -y
    
    # Start PostgreSQL service
    echo "🔄 Starting PostgreSQL service..."
    sudo service postgresql start
    sudo systemctl enable postgresql
    
    echo "✅ PostgreSQL installation complete!"
    echo ""
    
    # Show version
    psql --version
fi

echo ""
echo "🔐 Setting up FlexiFinance database and user..."

# Create database and user (idempotent)
sudo -u postgres psql << EOF
-- Drop existing user and database if they exist (for clean setup)
DROP USER IF EXISTS flexifinance_user;
DROP DATABASE IF EXISTS flexifinance;

-- Create user and database
CREATE USER flexifinance_user WITH PASSWORD 'flexifinance_password';
CREATE DATABASE flexifinance OWNER flexifinance_user;
GRANT ALL PRIVILEGES ON DATABASE flexifinance TO flexifinance_user;
\q
EOF

echo "✅ Database setup complete!"
echo ""

# Test database connection
echo "🧪 Testing database connection..."
if psql -h localhost -U flexifinance_user -d flexifinance -c "SELECT version();" &> /dev/null; then
    echo "✅ Database connection test successful!"
    echo ""
    
    # Show database info
    echo "📋 Database Details:"
    echo "   Database: flexifinance"
    echo "   User: flexifinance_user"
    echo "   Password: flexifinance_password"
    echo "   Host: localhost"
    echo "   Port: 5432"
    echo "   Connection URL:"
    echo "   postgresql://flexifinance_user:flexifinance_password@localhost:5432/flexifinance"
    echo ""
    
    # Show connection commands
    echo "🔗 Connection Commands:"
    echo "   Connect to database:"
    echo "   psql -h localhost -U flexifinance_user -d flexifinance"
    echo ""
    echo "   Test connection:"
    echo "   psql -h localhost -U flexifinance_user -d flexifinance -c 'SELECT version();'"
    
else
    echo "❌ Database connection test failed!"
    echo "   Please check your PostgreSQL configuration."
    echo ""
    echo "🔧 Troubleshooting:"
    echo "   1. Check if PostgreSQL service is running:"
    echo "      sudo service postgresql status"
    echo ""
    echo "   2. Check PostgreSQL logs:"
    echo "      sudo tail -f /var/log/postgresql/postgresql-*-main.log"
    echo ""
    echo "   3. Check PostgreSQL configuration:"
    echo "      sudo nano /etc/postgresql/*/main/postgresql.conf"
    echo "      # Ensure: listen_addresses = 'localhost'"
    echo ""
    echo "   4. Restart PostgreSQL:"
    echo "      sudo service postgresql restart"
fi

echo ""
echo "🎉 PostgreSQL setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Copy this connection string to your .env file:"
echo "   DATABASE_URL=postgresql://flexifinance_user:flexifinance_password@localhost:5432/flexifinance"
echo ""
echo "2. Run Django migrations:"
echo "   python manage.py migrate"
echo ""
echo "3. Start your Django development server:"
echo "   python manage.py runserver 0.0.0.0:8000"