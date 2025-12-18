# PostgreSQL Setup Guide for FlexiFinance

This guide will help you set up PostgreSQL for your FlexiFinance Django project.

## Prerequisites

1. **Install PostgreSQL** on your system:
   - **Windows**: Download from [postgresql.org](https://www.postgresql.org/download/windows/)
   - **macOS**: `brew install postgresql` or download from [postgresql.org](https://www.postgresql.org/download/macosx/)
   - **Linux (Ubuntu/Debian)**: `sudo apt install postgresql postgresql-contrib`
   - **Linux (CentOS/RHEL)**: `sudo yum install postgresql-server postgresql-contrib`

2. **Start PostgreSQL service**:
   - **Windows**: Services → PostgreSQL → Start
   - **macOS**: `brew services start postgresql`
   - **Linux**: `sudo systemctl start postgresql`

## Step-by-Step Setup

### 1. Create Database and User

Open PostgreSQL command line (psql) as postgres user:

```bash
# Windows/macOS/Linux
psql -U postgres
```

Run these SQL commands:

```sql
-- Create database
CREATE DATABASE flexifinance;

-- Create user
CREATE USER flexifinance_user WITH PASSWORD 'your_secure_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE flexifinance TO flexifinance_user;

-- Connect to the database
\c flexifinance

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO flexifinance_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO flexifinance_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO flexifinance_user;

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO flexifinance_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO flexifinance_user;

-- Exit psql
\q
```

### 2. Configure Environment Variables

Copy the example environment file:

```bash
# Copy .env.example to .env
cp .env.example .env
```

Edit the `.env` file and update these PostgreSQL settings:

```bash
# PostgreSQL Database Configuration
DB_NAME=flexifinance
DB_USER=flexifinance_user
DB_PASSWORD=your_secure_password  # Use the password you created above
DB_HOST=localhost
DB_PORT=5432
```

### 3. Run Database Migrations

Now that PostgreSQL is configured, run the migrations:

```bash
# Make migrations (if you made any changes to models)
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

### 4. Test the Connection

Test if the database connection works:

```bash
python manage.py shell
```

In the Django shell, run:

```python
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute("SELECT 1")
    print("Database connection successful!")
```

## Troubleshooting

### Common Issues and Solutions

1. **Connection Refused Error**:
   - Ensure PostgreSQL service is running
   - Check if PostgreSQL is listening on the correct port (5432)
   - Verify firewall settings allow connections on port 5432

2. **Authentication Failed Error**:
   - Double-check username and password in your `.env` file
   - Ensure the user exists in PostgreSQL: `\du` in psql
   - Check pg_hba.conf for authentication method (should be md5 or scram-sha-256)

3. **Database Does Not Exist Error**:
   - Ensure you created the database: `\l` in psql to list databases
   - Check database name spelling in your `.env` file

4. **Permission Denied Error**:
   - Ensure the user has proper privileges on the database
   - Run the GRANT commands from Step 1 again

### Check PostgreSQL Status

```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql  # Linux
brew services list | grep postgresql  # macOS

# Check PostgreSQL processes
ps aux | grep postgres

# Check PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-*.log  # Linux
```

### Reset PostgreSQL (if needed)

If you need to start fresh:

```sql
-- Drop and recreate database
DROP DATABASE IF EXISTS flexifinance;
CREATE DATABASE flexifinance;
```

## Development Workflow

### Starting the Development Server

```bash
# With your PostgreSQL database configured
python manage.py runserver
```

### Running Tests

```bash
# Run tests with PostgreSQL
python manage.py test
```

### Creating Backups

```bash
# Backup database
pg_dump -U flexifinance_user -h localhost flexifinance > backup.sql

# Restore database
psql -U flexifinance_user -h localhost flexifinance < backup.sql
```

## Production Considerations

### For Production Deployment

1. **Use Strong Passwords**: Never use default passwords in production
2. **Enable SSL/TLS**: Configure PostgreSQL for secure connections
3. **Connection Pooling**: Consider using connection pooling for better performance
4. **Regular Backups**: Set up automated database backups
5. **Monitor Performance**: Use tools like pgAdmin or PostgreSQL monitoring

### Example Production Settings

```python
# In production.py or settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'sslmode': 'require',
            'connect_timeout': 10,
        },
        'CONN_MAX_AGE': 600,
        'TEST': {
            'NAME': 'test_flexifinance',
        },
    }
}
```

## Additional Tools

### PostgreSQL GUI Clients

- **pgAdmin**: Web-based PostgreSQL administration tool
- **DBeaver**: Universal database tool
- **DataGrip**: JetBrains database IDE
- **Postico**: macOS PostgreSQL client

### Django Extensions for PostgreSQL

```bash
# Install PostgreSQL-specific Django extensions
pip install django-postgres-extra
pip install django-pgfields
```

## Verification Checklist

- [ ] PostgreSQL installed and running
- [ ] Database `flexifinance` created
- [ ] User `flexifinance_user` created with proper privileges
- [ ] `.env` file configured with correct PostgreSQL settings
- [ ] Migrations applied successfully
- [ ] Django development server starts without database errors
- [ ] Can access Django admin (if superuser created)

## Next Steps

Once PostgreSQL is set up and working:

1. **Run the development server**: `python manage.py runserver`
2. **Access the application**: http://localhost:8000
3. **Access Django admin**: http://localhost:8000/admin/
4. **Test all functionality** to ensure it works with PostgreSQL

## Support

If you encounter any issues:

1. Check the PostgreSQL logs for detailed error messages
2. Verify all configuration settings are correct
3. Ensure PostgreSQL service is running
4. Check Django logs for connection errors

For additional help, refer to:
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Django Database Settings](https://docs.djangoproject.com/en/stable/ref/settings/#databases)
- [psycopg2 Documentation](https://www.psycopg.org/docs/)