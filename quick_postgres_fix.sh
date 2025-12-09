#!/bin/bash

echo "🔧 Quick PostgreSQL Fix for WSL"
echo "================================"

# Stop all PostgreSQL services
echo "🛑 Stopping PostgreSQL services..."
sudo service postgresql stop 2>/dev/null || true
sudo service postgresql@16-main stop 2>/dev/null || true
sudo pkill -f postgres 2>/dev/null || true

# Find PostgreSQL config directory
PG_CONF_DIR=$(find /etc/postgresql -name "postgresql.conf" | head -1 | xargs dirname)
echo "📁 PostgreSQL config directory: $PG_CONF_DIR"

# Fix port in postgresql.conf
echo "🔧 Fixing PostgreSQL port..."
sudo sed -i 's/^#*port.*/port = 5432/' $PG_CONF_DIR/postgresql.conf
sudo sed -i 's/^#*listen_addresses.*/listen_addresses = '\''localhost'\''/' $PG_CONF_DIR/postgresql.conf

# Fix authentication in pg_hba.conf
echo "🔐 Fixing authentication..."
sudo cat > $PG_CONF_DIR/pg_hba.conf << 'EOF'
# PostgreSQL Client Authentication Configuration File

# "local" is for Unix domain socket connections only
local   all             postgres                                peer
local   all             all                                     peer

# IPv4 local connections:
host    all             all             127.0.0.1/32            md5

# IPv6 local connections:
host    all             all             ::1/128                 md5
EOF

# Start PostgreSQL
echo "🚀 Starting PostgreSQL..."
sudo service postgresql start

# Wait a moment for service to start
sleep 3

# Check status
echo "📊 Checking PostgreSQL status..."
sudo service postgresql status

# Test connection
echo "🧪 Testing connection..."
if sudo -u postgres psql -c "SELECT version();" &> /dev/null; then
    echo "✅ PostgreSQL is working!"
    
    # Recreate our database and user
    echo "🔐 Setting up FlexiFinance database..."
    sudo -u postgres psql << 'EOF'
DROP USER IF EXISTS flexifinance_user;
DROP DATABASE IF EXISTS flexifinance;
CREATE USER flexifinance_user WITH PASSWORD 'flexifinance_password';
CREATE DATABASE flexifinance OWNER flexifinance_user;
GRANT ALL PRIVILEGES ON DATABASE flexifinance TO flexifinance_user;
\q
EOF
    
    # Test our database connection
    echo "🧪 Testing FlexiFinance database connection..."
    if PGPASSWORD=flexifinance_password psql -h localhost -U flexifinance_user -d flexifinance -c "SELECT version();" &> /dev/null; then
        echo "✅ FlexiFinance database is working!"
        echo ""
        echo "🎉 SUCCESS! Database setup complete!"
        echo "📋 Connection details:"
        echo "   Database: flexifinance"
        echo "   User: flexifinance_user"
        echo "   Password: flexifinance_password"
        echo "   Host: localhost"
        echo "   Port: 5432"
        echo "   Connection URL:"
        echo "   postgresql://flexifinance_user:flexifinance_password@localhost:5432/flexifinance"
    else
        echo "⚠️  FlexiFinance database connection failed. You may need to restart PostgreSQL:"
        echo "   sudo service postgresql restart"
    fi
else
    echo "❌ PostgreSQL is not working. Check logs:"
    echo "   sudo tail -50 /var/log/postgresql/postgresql-*-main.log"
fi

echo ""
echo "🔗 Next steps:"
echo "1. Add to your .env file:"
echo "   DATABASE_URL=postgresql://flexifinance_user:flexifinance_password@localhost:5432/flexifinance"
echo ""
echo "2. Run Django migrations:"
echo "   python manage.py migrate"