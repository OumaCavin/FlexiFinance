# WSL PostgreSQL Fix Guide

## Current Issues Identified
1. PostgreSQL is running on port 5433 (not standard 5432)
2. PostgreSQL service authentication issues
3. Multiple PostgreSQL instances may be running

## Immediate Fix Steps

### Step 1: Stop All PostgreSQL Services
```bash
# Stop all PostgreSQL services
sudo service postgresql stop
sudo service postgresql@16-main stop 2>/dev/null || true

# Kill any PostgreSQL processes
sudo pkill -f postgres
```

### Step 2: Check PostgreSQL Configuration
```bash
# Check which PostgreSQL configuration is being used
sudo -u postgres psql -c "SHOW config_file;"
sudo -u postgres psql -c "SHOW port;"

# If above fails, check manually:
cat /etc/postgresql/*/main/postgresql.conf | grep -E "^port|^listen_addresses"
```

### Step 3: Fix PostgreSQL Port Configuration
```bash
# Find the correct PostgreSQL config file
sudo find /etc/postgresql -name "postgresql.conf"

# Edit the main config file (adjust version if different)
sudo nano /etc/postgresql/16/main/postgresql.conf
```

### Step 4: In postgresql.conf, ensure these settings:
```bash
# Find these lines and ensure they are set correctly:
port = 5432
listen_addresses = 'localhost'
```

### Step 5: Fix Authentication Configuration
```bash
# Edit pg_hba.conf
sudo nano /etc/postgresql/16/main/pg_hba.conf
```

### In pg_hba.conf, replace the content with:
```bash
# PostgreSQL Client Authentication Configuration File
# TYPE  DATABASE        USER            ADDRESS                 METHOD

# "local" is for Unix domain socket connections only
local   all             postgres                                peer
local   all             all                                     peer

# IPv4 local connections:
host    all             all             127.0.0.1/32            md5

# IPv6 local connections:
host    all             all             ::1/128                 md5
```

### Step 6: Reset postgres User Password
```bash
# Switch to postgres user and reset password
sudo -u postgres psql
```

In psql console, run:
```sql
\password postgres
-- Enter a new password when prompted
\q
```

### Step 7: Start PostgreSQL Service
```bash
# Start PostgreSQL service
sudo service postgresql start

# Check status
sudo service postgresql status

# Check if it's listening on the correct port
sudo netstat -tlnp | grep :5432
```

### Step 8: Test Connection
```bash
# Test connection as postgres user
sudo -u postgres psql

# Test connection as flexifinance_user
psql -h localhost -U flexifinance_user -d flexifinance

# Test with password
PGPASSWORD=flexifinance_password psql -h localhost -U flexifinance_user -d flexifinance -c "SELECT version();"
```

## Alternative Quick Fix (If Above Doesn't Work)

### Option A: Use Socket Connection
```bash
# Connect using Unix socket (no TCP/IP)
sudo -u postgres psql
```

### Option B: Recreate Everything
```bash
# Stop PostgreSQL
sudo service postgresql stop

# Remove existing data (WARNING: This deletes all data)
sudo rm -rf /var/lib/postgresql/16/main/*

# Reinitialize database
sudo -u postgres /usr/lib/postgresql/16/bin/initdb -D /var/lib/postgresql/16/main

# Start PostgreSQL
sudo service postgresql start

# Set postgres password
sudo -u postgres psql
\password postgres
\q

# Create our database and user
sudo -u postgres psql << EOF
CREATE USER flexifinance_user WITH PASSWORD 'flexifinance_password';
CREATE DATABASE flexifinance OWNER flexifinance_user;
GRANT ALL PRIVILEGES ON DATABASE flexifinance TO flexifinance_user;
\q
EOF
```

## Debugging Commands

```bash
# Check PostgreSQL processes
ps aux | grep postgres

# Check PostgreSQL logs
sudo tail -50 /var/log/postgresql/postgresql-16-main.log

# Check PostgreSQL configuration
sudo -u postgres psql -c "SHOW ALL;"

# Check port usage
sudo netstat -tlnp | grep postgres

# Check PostgreSQL data directory
sudo -u postgres psql -c "SHOW data_directory;"
```

## Expected Final Configuration

After fixes, you should have:
- PostgreSQL running on port 5432
- User: `flexifinance_user`
- Password: `flexifinance_password`
- Database: `flexifinance`
- Connection string: `postgresql://flexifinance_user:flexifinance_password@localhost:5432/flexifinance`
