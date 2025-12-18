# PostgreSQL Setup for WSL (Ubuntu)

This guide will help you set up PostgreSQL on WSL (Windows Subsystem for Linux) for the FlexiFinance project.

## 1. Check if PostgreSQL is Already Installed

### Check PostgreSQL installation:
```bash
# Check if PostgreSQL is installed
which psql
dpkg -l | grep postgresql

# Check if PostgreSQL service is running
sudo service postgresql status
```

### If PostgreSQL is already installed:
```bash
# PostgreSQL is installed - check service status
sudo service postgresql status

# If not running, start it:
sudo service postgresql start
sudo systemctl enable postgresql

# Skip to "Create Database User and Database" section
```

## 2. Install PostgreSQL in WSL (only if not already installed)

### Update package list:
```bash
sudo apt update
```

### Install PostgreSQL:
```bash
sudo apt install postgresql postgresql-contrib
```

### Start PostgreSQL service:
```bash
sudo service postgresql start
```

### Enable PostgreSQL to start on boot:
```bash
sudo systemctl enable postgresql
```

## 2. Create Database User and Database

### Switch to postgres user:
```bash
sudo -u postgres psql
```

### Create the database user with password:
```sql
CREATE USER flexifinance_user WITH PASSWORD 'flexifinance_password';
```

### Create the database:
```sql
CREATE DATABASE flexifinance OWNER flexifinance_user;
```

### Grant privileges:
```sql
GRANT ALL PRIVILEGES ON DATABASE flexifinance TO flexifinance_user;
```

### Exit psql:
```sql
\q
```

## 3. Test the Connection

### Test database connection:
```bash
psql -h localhost -U flexifinance_user -d flexifinance
```

### If prompted for password, enter: `flexifinance_password`

### You should see the postgres prompt:
```
flexifinance=> 
```

### Exit:
```sql
\q
```

## 4. Update .env Configuration

Add this to your `.env` file:
```env
# Database Configuration (PostgreSQL)
DATABASE_URL=postgresql://flexifinance_user:flexifinance_password@localhost:5432/flexifinance
```

## 5. Optional: Install pgAdmin (GUI for PostgreSQL)

### Install pgAdmin:
```bash
# Add pgAdmin repository
curl https://www.pgadmin.org/static/packages_pgadmin_org.pub | sudo apt-key add -
sudo sh -c 'echo "deb https://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'

# Update package list
sudo apt update

# Install pgAdmin
sudo apt install pgadmin4
```

### Access pgAdmin:
- Open browser and go to: `http://localhost/pgadmin4`
- Default login: `postgres` user (same password as system)

## 6. Troubleshooting

### If PostgreSQL service won't start:
```bash
sudo service postgresql status
sudo service postgresql restart
```

### If you get connection errors:
```bash
# Check if PostgreSQL is listening on localhost
sudo netstat -tlnp | grep :5432

# Check PostgreSQL configuration
sudo nano /etc/postgresql/14/main/postgresql.conf
# Ensure: listen_addresses = 'localhost'
```

### If authentication fails:
```bash
# Edit pg_hba.conf
sudo nano /etc/postgresql/14/main/pg_hba.conf
# Add or modify line:
# local   all             all                                     md5
```

### Restart PostgreSQL after config changes:
```bash
sudo service postgresql restart
```

## 7. Quick Setup Script (with Installation Checks)

Create a script to automate the setup with proper checks:

```bash
# Create setup script
nano ~/setup_postgres.sh
```

Add this content:
```bash
#!/bin/bash

echo "Setting up PostgreSQL for FlexiFinance..."

# Check if PostgreSQL is already installed
if command -v psql &> /dev/null; then
    echo "✅ PostgreSQL is already installed!"
    
    # Check if service is running
    if sudo service postgresql status &> /dev/null; then
        echo "✅ PostgreSQL service is running"
    else
        echo "🔄 Starting PostgreSQL service..."
        sudo service postgresql start
        sudo systemctl enable postgresql
    fi
else
    echo "📦 PostgreSQL not found. Installing..."
    
    # Update packages
    sudo apt update
    
    # Install PostgreSQL
    sudo apt install postgresql postgresql-contrib -y
    
    # Start PostgreSQL service
    sudo service postgresql start
    sudo systemctl enable postgresql
    
    echo "✅ PostgreSQL installation complete!"
fi

# Create user and database (idempotent)
echo "🔐 Setting up database user and database..."
sudo -u postgres psql << EOF
-- Drop existing user and database if they exist
DROP USER IF EXISTS flexifinance_user;
DROP DATABASE IF EXISTS flexifinance;

-- Create user and database
CREATE USER flexifinance_user WITH PASSWORD 'flexifinance_password';
CREATE DATABASE flexifinance OWNER flexifinance_user;
GRANT ALL PRIVILEGES ON DATABASE flexifinance TO flexifinance_user;
\q
EOF

echo "✅ Database setup complete!"
echo "📋 Database Details:"
echo "   Database: flexifinance"
echo "   User: flexifinance_user"
echo "   Password: flexifinance_password"
echo "   Connection: postgresql://flexifinance_user:flexifinance_password@localhost:5432/flexifinance"

# Test connection
echo "🧪 Testing database connection..."
if psql -h localhost -U flexifinance_user -d flexifinance -c "SELECT version();" &> /dev/null; then
    echo "✅ Database connection test successful!"
else
    echo "❌ Database connection test failed. Please check your configuration."
fi
```

Make it executable and run:
```bash
chmod +x ~/setup_postgres.sh
~/setup_postgres.sh
```

## 8. Windows Integration (Optional)

### From Windows Command Prompt:
```cmd
wsl sudo -u postgres psql -c "SELECT version();"
```

### Using Windows Terminal:
```powershell
wsl sudo -u postgres psql -d flexifinance -U flexifinance_user
```

## 9. Production Considerations

For production deployment, consider:
- **Stronger passwords**: Use generate strong passwords
- **SSL/TLS**: Enable encrypted connections
- **Firewall**: Configure proper firewall rules
- **Backup strategy**: Regular database backups
- **Performance tuning**: Optimize PostgreSQL configuration

## 10. Verification Commands

```bash
# Check PostgreSQL status
sudo service postgresql status

# List databases
sudo -u postgres psql -c "\l"

# List users
sudo -u postgres psql -c "\du"

# Connect to flexifinance database
sudo -u postgres psql -d flexifinance -c "\dt"
```

## Summary

After following this guide, you'll have:
- ✅ PostgreSQL installed and running on WSL
- ✅ Database user: `flexifinance_user`
- ✅ Database: `flexifinance`
- ✅ Connection string: `postgresql://flexifinance_user:flexifinance_password@localhost:5432/flexifinance`
- ✅ Ready for Django migrations and development