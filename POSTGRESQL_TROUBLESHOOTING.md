# PostgreSQL Connection Troubleshooting

Your database and user were created successfully, but the connection test failed. This is a common authentication issue.

## Issue Analysis
The database `flexifinance` and user `flexifinance_user` were created successfully, but PostgreSQL authentication configuration needs adjustment.

## Quick Fix Steps

### 1. Check Current PostgreSQL Configuration
```bash
# Check PostgreSQL service status
sudo service postgresql status

# Check PostgreSQL version and configuration
sudo -u postgres psql -c "SHOW listen_addresses;"
sudo -u postgres psql -c "SHOW port;"
```

### 2. Update Authentication Configuration
```bash
# Edit PostgreSQL authentication configuration
sudo nano /etc/postgresql/16/main/pg_hba.conf
```

### 3. In pg_hba.conf, find and update these lines:

**Find these lines (they should be near the top):**
```bash
# Database administrative login by Unix domain socket
local   all             postgres                                peer

# "local" is for Unix domain socket connections only
local   all             all                                     peer
```

**Replace them with:**
```bash
# Database administrative login by Unix domain socket
local   all             postgres                                md5

# "local" is for Unix domain socket connections only
local   all             all                                     md5

# IPv4 local connections:
host    all             all             127.0.0.1/32            md5

# IPv6 local connections:
host    all             all             ::1/128                 md5
```

### 4. Restart PostgreSQL Service
```bash
# Restart PostgreSQL to apply changes
sudo service postgresql restart

# Verify service is running
sudo service postgresql status
```

### 5. Test Connection Again
```bash
# Test connection with password prompt
psql -h localhost -U flexifinance_user -d flexifinance

# Test connection from command line (will prompt for password)
psql -h localhost -U flexifinance_user -d flexifinance -c "SELECT version();"

# Test connection using environment variable
PGPASSWORD=flexifinance_password psql -h localhost -U flexifinance_user -d flexifinance -c "SELECT current_database(), current_user;"
```

### 6. Alternative Quick Fix (if above doesn't work)

Create a `.pgpass` file for passwordless authentication:

```bash
# Create .pgpass file
echo "localhost:5432:flexifinance:flexifinance_user:flexifinance_password" > ~/.pgpass

# Set proper permissions
chmod 600 ~/.pgpass

# Test connection
psql -h localhost -U flexifinance_user -d flexifinance -c "SELECT version();"
```

### 7. Verify Database Creation

```bash
# Connect as postgres user and verify
sudo -u postgres psql -c "\l" | grep flexifinance
sudo -u postgres psql -c "\du" | grep flexifinance_user

# Test from Django
cd django-microfinance-mpsa
python manage.py dbshell
```

### 8. If Still Having Issues

```bash
# Check PostgreSQL logs for detailed error information
sudo tail -50 /var/log/postgresql/postgresql-16-main.log

# Check if PostgreSQL is listening on the correct port
sudo netstat -tlnp | grep :5432

# Test with localhost explicitly
psql -h 127.0.0.1 -U flexifinance_user -d flexifinance
```

## Expected Output After Fix

When working correctly, you should see:
```
flexifinance=> SELECT version();
                                                  version
--------------------------------------------------------------------------------------------------------------
 PostgreSQL 16.11 (Ubuntu 16.11-0ubuntu0.24.04.1) on x86_64-pc-linux-gnu, compiled by gcc (Ubuntu 13.3.0-1ubuntu2~24.04) 13.3.0, 64-bit
(1 row)

flexifinance=> \q
```

## Update Your .env File

Once the connection works, your `.env` file should have:
```env
DATABASE_URL=postgresql://flexifinance_user:flexifinance_password@localhost:5432/flexifinance
```

## Next Steps After Fix

1. Test the connection with the commands above
2. Update your `.env` file with the DATABASE_URL
3. Run Django migrations: `python manage.py migrate`
4. Start development server: `python manage.py runserver 0.0.0.0:8000`

## Why This Happens

PostgreSQL by default uses "peer" authentication for local connections, which requires the system username to match the database username. By changing to "md5" authentication, we enable password-based authentication which works with different usernames.
